# SS RAG — Project Context

## What is this?

A **fully offline RAG (Retrieval-Augmented Generation) system** for the IPC (International Pentecostal Church) Sunday School curriculum. It lets students and teachers ask questions about their curriculum PDFs (textbooks, teacher guides) and get accurate, cited answers using a local LLM — no internet or API keys required.

---

## Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Embeddings | `nomic-embed-text` via Ollama | Local, no API key |
| LLM | `llama3.2` via Ollama | Local, runs offline |
| Vector DB | ChromaDB | Persistent, stored in `chroma_db/` |
| PDF Parsing | PyMuPDF + pdfplumber | Extracts text + lesson structure |
| Framework | LangChain (LCEL) | `langchain-core`, `langchain-ollama`, `langchain-community` |
| Web UI | Streamlit (`app.py`) | Optional |
| CLI | Python (`cli.py`) | Primary interface |
| Conda Env | `ss-rag` | Python 3.11 |

---

## Project Files

```
SS RAG/
├── pdf_parser.py       # Parses PDFs, detects lesson boundaries, chunks text
├── indexer.py          # Builds ChromaDB from parsed PDFs
├── query_engine.py     # RAG query logic (LCEL pipeline: retriever | prompt | llm)
├── cli.py              # Interactive terminal interface
├── app.py              # Streamlit web interface
├── setup.py            # First-time setup automation
├── .env                # Local config (gitignored)
├── .env.example        # Config template
├── requirements.txt    # Python dependencies
├── ARCHITECTURE.md     # Detailed system architecture doc
├── pdfs/               # Source PDF files (gitignored, add your own)
└── chroma_db/          # Vector database (gitignored, regenerate with indexer.py)
```

---

## Configuration (`.env`)

```env
CHROMA_PERSIST_DIRECTORY=./chroma_db
PDF_DIRECTORY=./pdfs
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=llama3.2
CHUNK_SIZE=600
CHUNK_OVERLAP=100
```

---

## How to Run

```bash
# 1. Activate environment
conda activate ss-rag

# 2. Start Ollama and pull models (one-time)
ollama serve
ollama pull nomic-embed-text
ollama pull llama3.2

# 3. Add PDFs to pdfs/ then build the vector DB (one-time or when PDFs change)
python indexer.py

# 4. Query
python cli.py              # Terminal interface
streamlit run app.py       # Web interface
```

---

## Query Modes

| Mode | Use For |
|---|---|
| `student` | Simple explanations, homework help |
| `teacher` | Teaching strategies, lesson planning |
| `exam_prep` | Key facts, practice questions, memory verses |
| `verse_lookup` | Find exact Bible verses and references |

**CLI commands:** `:mode <mode>`, `:grade <1-13>`, `:curriculum <IPC|Radiant Life|Christian Identity>`, `:clear`

---

## Chunking Strategy

- **Primary:** Lesson-based chunking — detects "Lesson X: Title" boundaries, preserves full lesson as one chunk
- **Fallback:** Fixed-size — 600 char chunks with 100 char overlap
- **Metadata per chunk:** `curriculum`, `grade`, `doc_type`, `lesson_number`, `lesson_title`, `page_number`, `exam_relevant`, `contains_verse`, `source_file`

---

## Supported Curricula

- **IPC** — International Pentecostal Church textbooks
- **Radiant Life**
- **Christian Identity**
- Grades 1–13

---

## Git Branches

| Branch | Purpose |
|---|---|
| `Initial` | Original OpenAI-based implementation |
| `local` | Current — fully local Ollama-based implementation |

---

## Key Design Decisions

- **Fully offline:** Replaced OpenAI (`text-embedding-3-small`, `gpt-4o-mini`) with Ollama (`nomic-embed-text`, `llama3.2`)
- **LCEL pipeline:** Upgraded from deprecated `RetrievalQA` chain to modern `retriever.invoke() → prompt | llm | StrOutputParser()` pattern
- **Large files gitignored:** `pdfs/` and `chroma_db/` excluded from git; regenerate DB with `python indexer.py`

---

## Future Roadmap

- [ ] Hybrid search (BM25 + vector)
- [ ] Query caching
- [ ] Malayalam language support
- [ ] Auto-quiz generator
- [ ] Progress tracking
- [ ] Mobile app
