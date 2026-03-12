"""
RAG Query Engine - Retrieve and generate answers from IPC curriculum
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

import chromadb
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class IPCRAGEngine:
    """RAG query engine for IPC Sunday School curriculum"""
    
    def __init__(self, persist_directory: str = "./chroma_db", 
                 collection_name: str = "ipc_curriculum"):
        load_dotenv()
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embeddings (local Ollama)
        self.embeddings = OllamaEmbeddings(
            model=os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')
        )
        
        # Initialize LLM (local Ollama)
        self.llm = ChatOllama(
            model=os.getenv('LLM_MODEL', 'llama3.2'),
            temperature=0.3  # Lower temperature for more factual responses
        )
        
        # Load vector store
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        
        # Create retrievers for different modes
        self.retrievers = {
            'default': self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            'exam_prep': self.vectorstore.as_retriever(
                search_kwargs={
                    "k": 8,
                    "filter": {"exam_relevant": True}
                }
            )
        }
        
        # Define prompts for different modes
        self.prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, PromptTemplate]:
        """Initialize prompts for different query modes"""
        
        # Student Mode - Clear, educational answers
        student_prompt = PromptTemplate(
            template="""You are a helpful Sunday School teaching assistant. Answer the student's question based ONLY on the provided context from the IPC curriculum textbooks.

Context from textbooks:
{context}

Student's Question: {question}

Instructions:
- Give a clear, easy-to-understand answer
- Use the exact content from the textbooks
- If the answer includes a Bible verse, quote it fully
- If the question asks about a memory verse, provide the complete verse
- If the information is not in the context, say "I don't have information about that in the curriculum materials"
- Keep the answer focused and relevant
- Use simple language appropriate for the student's grade level

Answer:""",
            input_variables=["context", "question"]
        )
        
        # Teacher Mode - Include teaching tips and cross-references
        teacher_prompt = PromptTemplate(
            template="""You are an experienced Sunday School curriculum coordinator helping a teacher. Answer based on the provided context from IPC curriculum materials.

Context from textbooks:
{context}

Teacher's Question: {question}

Instructions:
- Provide comprehensive information including teaching approaches
- Reference specific lessons, grades, and page numbers when available
- Suggest cross-references to related content if visible in context
- Include practical teaching tips from teacher guides when available
- Be thorough and professional

Answer:""",
            input_variables=["context", "question"]
        )
        
        # Exam Prep Mode - Focus on testable content
        exam_prep_prompt = PromptTemplate(
            template="""You are an exam preparation assistant for IPC Sunday School students. Answer based ONLY on exam-relevant content from the curriculum.

Context from textbooks (exam-relevant sections):
{context}

Student's Question: {question}

Instructions:
- Focus on key facts, concepts, and memory verses that would be tested
- Provide complete memory verses when asked
- Break down complex concepts into testable points
- If asked for practice questions, create them based on the provided context
- Always cite which lesson or grade the information comes from
- If something isn't in the exam-relevant content, say so clearly

Answer:""",
            input_variables=["context", "question"]
        )
        
        # Verse Lookup Mode - Specialized for finding Bible verses
        verse_prompt = PromptTemplate(
            template="""You are a memory verse reference assistant for IPC Sunday School curriculum. Find and provide the exact Bible verse from the context.

Context from textbooks:
{context}

Question: {question}

Instructions:
- Provide the complete, exact verse as written in the curriculum
- Include the Bible reference (book, chapter, verse)
- If multiple verses match, provide all of them with their lesson/grade references
- If the verse is not found in the context, say "This verse is not in the curriculum materials I have access to"

Answer:""",
            input_variables=["context", "question"]
        )
        
        return {
            'student': student_prompt,
            'teacher': teacher_prompt,
            'exam_prep': exam_prep_prompt,
            'verse_lookup': verse_prompt
        }
    
    def query(self, 
             question: str, 
             mode: str = 'student',
             filters: Optional[Dict[str, Any]] = None,
             k: int = 5) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User's question
            mode: Query mode ('student', 'teacher', 'exam_prep', 'verse_lookup')
            filters: Metadata filters (e.g., {'grade': 5, 'curriculum': 'IPC'})
            k: Number of chunks to retrieve
            
        Returns:
            Dictionary with answer and source information
        """
        
        # Select appropriate prompt
        prompt = self.prompts.get(mode, self.prompts['student'])
        
        # Build search kwargs
        search_kwargs = {"k": k}
        if filters:
            search_kwargs["filter"] = filters
        
        # Create retriever with filters
        retriever = self.vectorstore.as_retriever(search_kwargs=search_kwargs)

        # Retrieve source documents for citation
        source_docs = retriever.invoke(question)

        # Format context from retrieved docs
        context = "\n\n".join([doc.page_content for doc in source_docs])

        # Build LCEL chain: prompt | llm | output parser
        chain = prompt | self.llm | StrOutputParser()

        # Get answer
        answer = chain.invoke({"context": context, "question": question})

        # Format response
        response = {
            'question': question,
            'answer': answer,
            'sources': self._format_sources(source_docs),
            'mode': mode
        }

        return response
    
    def _format_sources(self, source_documents: List) -> List[Dict[str, Any]]:
        """Format source documents for display"""
        
        sources = []
        
        for doc in source_documents:
            source_info = {
                'text_preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                'metadata': doc.metadata
            }
            sources.append(source_info)
        
        return sources
    
    def search_memory_verses(self, grade: Optional[int] = None, 
                            curriculum: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for all memory verses, optionally filtered by grade/curriculum"""
        
        filters = {"contains_verse": True}
        
        if grade:
            filters['grade'] = grade
        if curriculum:
            filters['curriculum'] = curriculum
        
        # Retrieve chunks with verses
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": 100,  # Get many results
                "filter": filters
            }
        )
        
        # Get relevant documents
        docs = retriever.get_relevant_documents("memory verse Bible verse")
        
        # Extract verse information
        verses = []
        for doc in docs:
            verses.append({
                'text': doc.page_content[:500],
                'lesson': doc.metadata.get('lesson_number'),
                'lesson_title': doc.metadata.get('lesson_title'),
                'grade': doc.metadata.get('grade'),
                'curriculum': doc.metadata.get('curriculum')
            })
        
        return verses
    
    def get_lesson_content(self, grade: int, lesson_number: int, 
                          curriculum: str = 'IPC') -> Dict[str, Any]:
        """Retrieve full content of a specific lesson"""
        
        filters = {
            'grade': grade,
            'lesson_number': lesson_number,
            'curriculum': curriculum
        }
        
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": 20,
                "filter": filters
            }
        )
        
        docs = retriever.get_relevant_documents(f"lesson {lesson_number} content")
        
        # Combine all chunks from this lesson
        full_content = "\n\n".join([doc.page_content for doc in docs])
        
        return {
            'grade': grade,
            'lesson_number': lesson_number,
            'curriculum': curriculum,
            'content': full_content,
            'metadata': docs[0].metadata if docs else {}
        }


def main():
    """Example usage"""
    
    print("="*60)
    print("IPC SUNDAY SCHOOL RAG QUERY ENGINE")
    print("="*60)
    print()
    
    # Initialize engine
    engine = IPCRAGEngine()
    
    # Example queries
    example_queries = [
        {
            'question': "What is the memory verse for Grade 5 Lesson 3?",
            'mode': 'verse_lookup',
            'filters': {'grade': 5}
        },
        {
            'question': "Explain the concept of salvation",
            'mode': 'student',
            'filters': {'curriculum': 'IPC'}
        },
        {
            'question': "What teaching activities are suggested for the Middler level?",
            'mode': 'teacher',
            'filters': None
        }
    ]
    
    for i, query_config in enumerate(example_queries, 1):
        print(f"\nExample {i}:")
        print(f"Question: {query_config['question']}")
        print(f"Mode: {query_config['mode']}")
        
        result = engine.query(
            question=query_config['question'],
            mode=query_config['mode'],
            filters=query_config['filters']
        )
        
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources: {len(result['sources'])} documents retrieved")
        print("-" * 60)


if __name__ == "__main__":
    main()
