# 📖 IPC Sunday School RAG System

A complete Retrieval-Augmented Generation (RAG) system for IPC Eastern Region Sunday School curriculum. Query textbooks, find memory verses, prepare for exams, and assist with lesson planning using AI.

## 🎯 Features

- **4 Query Modes:**
  - 🎓 **Student Mode** - Clear answers for homework and study
  - 👨‍🏫 **Teacher Mode** - Lesson planning and teaching strategies
  - 📝 **Exam Prep Mode** - Focus on testable content
  - 📜 **Verse Lookup** - Find and reference Bible verses

- **Smart Filtering:**
  - Filter by curriculum - IPC (Still in progress for other curriculum)
  - Filter by grade (1-13)
  - Filter by document type (textbook, teacher guide, student guide)

- **Multiple Interfaces:**
  - Web UI (Streamlit)

## 🏗️ Architecture

```
PDFs → Parser → Chunks → Embeddings → ChromaDB → RAG Engine → User
                                           ↓
                                     Google Gemini API
```

**Key Components:**
- **PDF Parser** - Extracts text and metadata from curriculum PDFs
- **Embeddings** - Google `models/embedding-001` for semantic search
- **Vector DB** - ChromaDB for local storage
- **LLM** - Gemini 2.0 Flash for answer generation

## 📋 Prerequisites

- Python 3.8+
- Google API key ([get one here](https://aistudio.google.com/apikey))
- PDF files of IPC curriculum

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# Required:
GOOGLE_API_KEY=your-api-key-here

# Optional configurations:
PDF_DIRECTORY=./pdfs                    # Where your PDF files are
CHROMA_PERSIST_DIRECTORY=./chroma_db   # Where to store the database
EMBEDDING_MODEL=models/embedding-001   # Embedding model
LLM_MODEL=gemini-2.0-flash             # Generation model
CHUNK_SIZE=600                          # Characters per chunk
CHUNK_OVERLAP=100                       # Overlap between chunks
```

### 3. Organize Your PDFs

Place all curriculum PDF files in the `pdfs/` directory:

```
pdfs/
├── IPC_Grade_1.pdf
├── IPC_Grade_2.pdf
├── IPC_Teacher_Guide_Grade_3.pdf
├── Radiant_Life_Middler.pdf
├── Christian_Identity_Textbook.pdf
└── ...
```

**Naming Convention:** Include curriculum name, grade, and document type in filename for better metadata extraction.

### 4. Build the Database

```bash
python indexer.py
```

This will:
- Parse all PDFs
- Extract lessons and metadata
- Generate embeddings
- Build the vector database

**Time estimate:** ~5-15 minutes depending on number of PDFs

## 🎛️ Configuration Options

### Embedding Models

**Current:** `models/embedding-001` (Google)
- Dimensions: 768
- Quality: Excellent

**Alternative:** `models/text-embedding-004`
- Dimensions: 768
- Quality: Best

### LLM Models

**Current:** `gemini-2.0-flash`
- Speed: Fast (1-2s)
- Quality: Excellent for RAG

**Alternative:** `gemini-2.0-pro`
- Speed: Slower (3-5s)
- Quality: Best (unnecessary for this use case)

### Chunking Strategy

**Current settings:**
- Chunk by lesson boundaries (smart)
- Fallback to 600 characters with 100 overlap
- Preserves lesson titles and numbers

**Adjustable in `.env`:**
```bash
CHUNK_SIZE=600        # Increase for more context per chunk
CHUNK_OVERLAP=100     # Increase to reduce boundary issues
```

## 🔒 Data Privacy

- **Local storage:** Vector database stored locally in `chroma_db/`
- **API calls:** Only query embeddings and LLM generation go to Google
- **Deletion:** Delete `chroma_db/` folder to remove all indexed data

## 🐛 Troubleshooting

### "No module named 'chromadb'"
```bash
pip install -r requirements.txt
```

### "Error loading engine"
Make sure you've run `python indexer.py` first to build the database.

### "GOOGLE_API_KEY not found"
Add your API key to `.env` file:
```bash
GOOGLE_API_KEY=your-api-key-here
```

### "No PDF files found"
Check that PDFs are in the correct directory (default: `./pdfs/`)

### Poor answer quality
Try:
1. Increase `k` (number of retrieved chunks) to 8-10
2. Use more specific questions
3. Add filters (grade, curriculum)
4. Check if the content exists in your indexed PDFs

### Out of memory during indexing
Process PDFs in batches:
```python
# Split pdfs/ into batches and run indexer.py multiple times
```

## 📈 Performance Tuning

### For Faster Queries
- Reduce `k` to 3-4 chunks
- Use `gemini-2.0-flash`

### For Better Accuracy
- Increase `k` to 8-10 chunks
- Add metadata filters
- Use `gemini-2.0-pro` for complex questions

## 🔄 Updating the Database

When new PDFs are added:

```bash
# Delete old database
rm -rf chroma_db/

# Re-index with new PDFs
python indexer.py
```

**Note:** This is necessary when:
- Adding new textbooks
- Curriculum updates
- Fixing PDF parsing issues

## 📚 Project Structure

```
.
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your configuration (git-ignored)
├── pdf_parser.py         # PDF parsing logic
├── indexer.py            # Database builder
├── query_engine.py       # RAG query engine
├── app.py                # Streamlit web interface
├── cli.py                # Command line interface
├── pdfs/                 # Your PDF files
├── chroma_db/            # Vector database (auto-generated)
└── README.md             # This file
```

## 🎓 Use Cases

1. **Student Exam Prep**
   - Practice questions
   - Memory verse review
   - Concept explanations

2. **Teacher Lesson Planning**
   - Teaching strategies
   - Activity suggestions
   - Cross-curriculum references

3. **Parent Support**
   - Understanding curriculum
   - Helping with homework
   - Tracking child's progress

4. **Church Administration**
   - Curriculum comparison
   - Onboarding new teachers
   - Exam question generation

## 🚧 Future Enhancements

- [ ] Multi-language support (Malayalam)
- [ ] Quiz generator
- [ ] Progress tracking
- [ ] Export to PDF/Word
- [ ] Mobile app
- [ ] Offline mode with local LLM

## 📝 License

This project is for educational use within the IPC Eastern Region Sunday School community.

## 🤝 Support

For questions or issues:
1. Check the troubleshooting section
2. Review example queries
3. Contact the developer

## 🙏 Acknowledgments

Built for the IPC Eastern Region Sunday School Association to support Christian education for grades 1-13.

---

**Last Updated:** February 2026
