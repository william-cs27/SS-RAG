"""
Streamlit Web Interface for IPC Sunday School RAG System
"""

import streamlit as st
import os
from dotenv import load_dotenv
from query_engine import IPCRAGEngine

# Load environment
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="IPC Sunday School Study Assistant",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_rag_engine():
    """Load RAG engine (cached)"""
    return IPCRAGEngine()


def main():
    # Header
    st.markdown('<h1 class="main-header">📖 IPC Sunday School Study Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about your curriculum, memory verses, and lessons</p>', unsafe_allow_html=True)
    
    # Initialize RAG engine
    try:
        engine = load_rag_engine()
    except Exception as e:
        st.error(f"Error loading RAG engine: {e}")
        st.info("Make sure you have run `python indexer.py` first to build the database!")
        return
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Mode selection
        mode = st.selectbox(
            "Select Mode",
            options=['student', 'teacher', 'exam_prep', 'verse_lookup'],
            format_func=lambda x: {
                'student': '🎓 Student Mode',
                'teacher': '👨‍🏫 Teacher Mode',
                'exam_prep': '📝 Exam Prep Mode',
                'verse_lookup': '📜 Verse Lookup Mode'
            }[x],
            help="Choose how you want answers formatted"
        )
        
        st.markdown("---")
        
        # Filters
        st.subheader("🔍 Filters")
        
        use_filters = st.checkbox("Enable Filters")
        
        filters = {}
        if use_filters:
            curriculum = st.selectbox(
                "Curriculum",
                options=['All', 'IPC', 'Radiant Life', 'Christian Identity'],
                index=0
            )
            if curriculum != 'All':
                filters['curriculum'] = curriculum
            
            grade = st.selectbox(
                "Grade",
                options=['All'] + list(range(1, 14)),
                index=0
            )
            if grade != 'All':
                filters['grade'] = grade
            
            doc_type = st.selectbox(
                "Document Type",
                options=['All', 'textbook', 'teacher_guide', 'student_guide'],
                index=0
            )
            if doc_type != 'All':
                filters['doc_type'] = doc_type
        
        st.markdown("---")
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            k = st.slider("Number of sources to retrieve", min_value=3, max_value=15, value=5)
        
        st.markdown("---")
        
        # Quick examples
        st.subheader("💡 Example Questions")
        
        example_questions = {
            'student': [
                "What is the memory verse for Grade 5 Lesson 3?",
                "Explain the concept of salvation",
                "What does Lesson 7 teach about prayer?"
            ],
            'teacher': [
                "What teaching activities are suggested for Grade 6?",
                "How should I teach about baptism to Grade 4 students?",
                "What topics does the Middler level cover?"
            ],
            'exam_prep': [
                "Give me 5 practice questions for Grade 8",
                "What are the key concepts for the Grade 10 exam?",
                "List all memory verses for Grade 6"
            ],
            'verse_lookup': [
                "Find all verses about love",
                "What is John 3:16 in the curriculum?",
                "Show me verses from the book of Psalms"
            ]
        }
        
        for q in example_questions.get(mode, []):
            if st.button(q, key=f"example_{q[:20]}"):
                st.session_state.example_question = q
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Query input
        question = st.text_area(
            "Ask your question:",
            value=st.session_state.get('example_question', ''),
            height=100,
            placeholder="e.g., What is the memory verse for Grade 5 Lesson 3?"
        )
        
        # Clear example question after use
        if 'example_question' in st.session_state:
            del st.session_state.example_question
        
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
        
        if search_button and question:
            with st.spinner("Searching curriculum..."):
                try:
                    # Query the engine
                    result = engine.query(
                        question=question,
                        mode=mode,
                        filters=filters if use_filters else None,
                        k=k
                    )
                    
                    # Display answer
                    st.markdown("### 💡 Answer")
                    st.markdown(result['answer'])
                    
                    # Display sources
                    st.markdown("---")
                    st.markdown("### 📚 Sources")
                    
                    for i, source in enumerate(result['sources'], 1):
                        with st.expander(f"Source {i}: {source['metadata'].get('lesson_title', 'Unknown Lesson')}"):
                            st.markdown("**Metadata:**")
                            metadata = source['metadata']
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Grade", metadata.get('grade', 'N/A'))
                            with col_b:
                                st.metric("Lesson", metadata.get('lesson_number', 'N/A'))
                            with col_c:
                                st.metric("Curriculum", metadata.get('curriculum', 'N/A'))
                            
                            st.markdown("**Content Preview:**")
                            st.text(source['text_preview'])
                
                except Exception as e:
                    st.error(f"Error processing query: {e}")
        
        elif search_button:
            st.warning("Please enter a question!")
    
    with col2:
        # Info panel
        st.markdown("### ℹ️ Mode Info")
        
        mode_info = {
            'student': {
                'emoji': '🎓',
                'title': 'Student Mode',
                'description': 'Get clear, easy-to-understand answers for your studies',
                'best_for': 'Homework help, concept explanations, verse memorization'
            },
            'teacher': {
                'emoji': '👨‍🏫',
                'title': 'Teacher Mode',
                'description': 'Access teaching tips, lesson plans, and cross-references',
                'best_for': 'Lesson planning, teaching strategies, curriculum overview'
            },
            'exam_prep': {
                'emoji': '📝',
                'title': 'Exam Prep Mode',
                'description': 'Focus on testable content and practice questions',
                'best_for': 'Annual exam preparation, key facts, memory verses'
            },
            'verse_lookup': {
                'emoji': '📜',
                'title': 'Verse Lookup',
                'description': 'Find specific Bible verses and their references',
                'best_for': 'Memory verse search, verse location, Bible study'
            }
        }
        
        info = mode_info[mode]
        st.markdown(f"## {info['emoji']} {info['title']}")
        st.write(info['description'])
        st.info(f"**Best for:** {info['best_for']}")
        
        # Statistics (if available)
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        # You can add database statistics here
        st.metric("Total Documents", "Available in DB")
        st.metric("Grades Covered", "1-13")
        st.metric("Curricula", "IPC, Radiant Life, Christian Identity")


if __name__ == "__main__":
    main()
