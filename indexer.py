"""
RAG Indexer - Build vector database from parsed PDFs
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from tqdm import tqdm

import chromadb
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

from pdf_parser import IPCPDFParser, DocumentChunk


class RAGIndexer:
    """Build and manage the RAG index for IPC curriculum"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        load_dotenv()
        
        self.persist_directory = persist_directory
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')
        
        # Initialize embeddings (local Ollama)
        self.embeddings = OllamaEmbeddings(
            model=self.embedding_model
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize parser
        self.parser = IPCPDFParser()
        
    def index_pdfs(self, pdf_directory: str, collection_name: str = "ipc_curriculum"):
        """Index all PDFs in a directory"""
        
        pdf_dir = Path(pdf_directory)
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {pdf_directory}")
            return
        
        print(f"Found {len(pdf_files)} PDF files to index")
        
        all_chunks = []
        
        # Parse all PDFs
        for pdf_path in tqdm(pdf_files, desc="Parsing PDFs"):
            chunks = self.parser.parse_pdf(
                str(pdf_path),
                chunk_size=int(os.getenv('CHUNK_SIZE', 600)),
                chunk_overlap=int(os.getenv('CHUNK_OVERLAP', 100))
            )
            all_chunks.extend(chunks)
        
        print(f"\nTotal chunks extracted: {len(all_chunks)}")
        
        if not all_chunks:
            print("No chunks extracted. Exiting.")
            return
        
        # Prepare data for ChromaDB
        texts = [chunk.text for chunk in all_chunks]
        metadatas = [chunk.metadata for chunk in all_chunks]
        ids = [f"chunk_{i}" for i in range(len(all_chunks))]
        
        # Create or get collection
        try:
            self.client.delete_collection(name=collection_name)
            print(f"Deleted existing collection: {collection_name}")
        except:
            pass
        
        print(f"\nCreating vector database...")
        
        # Create vector store
        vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            ids=ids,
            collection_name=collection_name,
            persist_directory=self.persist_directory
        )
        
        print(f"✅ Successfully indexed {len(all_chunks)} chunks into '{collection_name}' collection")
        print(f"   Database location: {self.persist_directory}")
        
        # Print statistics
        self._print_statistics(all_chunks)
        
        return vectorstore
    
    def _print_statistics(self, chunks: List[DocumentChunk]):
        """Print indexing statistics"""
        
        print("\n" + "="*60)
        print("INDEXING STATISTICS")
        print("="*60)
        
        # Count by curriculum
        curricula = {}
        grades = {}
        doc_types = {}
        lessons = set()
        
        for chunk in chunks:
            curriculum = chunk.metadata.get('curriculum', 'unknown')
            curricula[curriculum] = curricula.get(curriculum, 0) + 1
            
            grade = chunk.metadata.get('grade')
            if grade:
                grades[grade] = grades.get(grade, 0) + 1
            
            doc_type = chunk.metadata.get('doc_type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            lesson = chunk.metadata.get('lesson_number')
            if lesson:
                lessons.add((curriculum, grade, lesson))
        
        print(f"\nTotal Chunks: {len(chunks)}")
        
        print(f"\nBy Curriculum:")
        for curr, count in sorted(curricula.items()):
            print(f"  {curr}: {count} chunks")
        
        print(f"\nBy Grade:")
        for grade, count in sorted(grades.items()):
            print(f"  Grade {grade}: {count} chunks")
        
        print(f"\nBy Document Type:")
        for dtype, count in sorted(doc_types.items()):
            print(f"  {dtype}: {count} chunks")
        
        print(f"\nTotal Unique Lessons: {len(lessons)}")
        print("="*60 + "\n")


def main():
    """Main indexing function"""
    
    load_dotenv()
    
    # Get configuration
    pdf_directory = os.getenv('PDF_DIRECTORY', './pdfs')
    persist_directory = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
    
    print("="*60)
    print("IPC SUNDAY SCHOOL RAG INDEXER")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  PDF Directory: {pdf_directory}")
    print(f"  Vector DB Directory: {persist_directory}")
    print(f"  Embedding Model: {os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')} (Ollama)")
    print(f"  Chunk Size: {os.getenv('CHUNK_SIZE', 600)}")
    print(f"  Chunk Overlap: {os.getenv('CHUNK_OVERLAP', 100)}")
    print()
    
    # Check if PDF directory exists
    if not Path(pdf_directory).exists():
        print(f"❌ Error: PDF directory '{pdf_directory}' does not exist!")
        print(f"   Please create it and add your PDF files.")
        return
    
    # Create indexer
    indexer = RAGIndexer(persist_directory=persist_directory)
    
    # Index PDFs
    vectorstore = indexer.index_pdfs(pdf_directory)
    
    if vectorstore:
        print("\n✅ Indexing complete! You can now run the query interface.")
    else:
        print("\n❌ Indexing failed. Please check the errors above.")


if __name__ == "__main__":
    main()
