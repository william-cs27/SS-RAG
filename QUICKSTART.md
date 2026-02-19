# 🚀 Quick Start Guide - IPC Sunday School RAG

Get up and running in 15 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] OpenAI API key (get from https://platform.openai.com/api-keys)
- [ ] PDF files downloaded
- [ ] 10GB free disk space
- [ ] Internet connection

## Installation (5 minutes)

### Step 1: Download the code

Extract the ZIP file or clone the repository to a folder.

### Step 2: Run setup script

```bash
# macOS/Linux
python3 setup.py

# Windows
python setup.py
```

This will:
- Check Python version
- Create necessary folders
- Setup .env file (you'll enter your API key)
- Install dependencies

**Alternative: Manual setup**

```bash
# Create folders
mkdir pdfs chroma_db

# Copy and edit environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Install dependencies
pip install -r requirements.txt
```

## Add Your PDFs (2 minutes)

Copy all curriculum PDFs into the `pdfs/` folder:

```
pdfs/
├── IPC_Grade_1.pdf
├── IPC_Grade_2.pdf
├── Radiant_Life_Middler.pdf
└── ...
```

**Tip:** Name files clearly with curriculum, grade, and type for better metadata extraction.

## Build the Database (5 minutes)

```bash
python indexer.py
```

You should see:
```
Found 25 PDF files to index
Parsing PDFs: 100%|████████| 25/25
Total chunks extracted: 2,847
✅ Successfully indexed 2,847 chunks
```

**Troubleshooting:**
- "OPENAI_API_KEY not found" → Add your key to .env file
- "No PDF files found" → Check pdfs/ folder has .pdf files

## Start Using It! (3 minutes)

### Option A: Web Interface (Easiest)

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser

**Try these questions:**
- "What is the memory verse for Grade 5 Lesson 3?"
- "Explain salvation in simple terms"
- "What topics does Grade 7 cover?"

### Option B: Command Line

```bash
# Interactive mode
python cli.py

# Ask a question
> What does Grade 6 teach about baptism?

# Change mode
> :mode exam_prep

# Filter by grade
> :grade 8

# Quit
> quit
```

### Option C: Python Code

```python
from query_engine import IPCRAGEngine

engine = IPCRAGEngine()

result = engine.query(
    question="What is the memory verse for Grade 5?",
    mode='verse_lookup',
    filters={'grade': 5}
)

print(result['answer'])
```

## Common First Questions

### For Students
```
What is the memory verse for Grade [X] Lesson [Y]?
Explain [concept] in simple terms
Give me a summary of Lesson [X]
Create 5 practice questions for Grade [X]
```

### For Teachers
```
What teaching activities are suggested for Grade [X]?
How should I teach [topic] to [grade level]?
What topics overlap between IPC and Radiant Life?
Show me the lesson plan for Grade [X] Lesson [Y]
```

### For Parents
```
What is my Grade [X] child learning this month?
Help me explain [concept] to my child
What memory verse should my child know?
```

## Configuration Tips

### Make answers shorter/longer

Edit `.env`:
```bash
CHUNK_SIZE=600    # Increase for longer answers
```

### Change the model

Edit `.env`:
```bash
LLM_MODEL=gpt-4o              # More expensive, better quality
LLM_MODEL=gpt-4o-mini         # Cheaper, good quality (default)
```

### Filter results

In web interface: Use sidebar filters
In CLI: Use `:grade 5` and `:curriculum IPC`
In Python: Pass `filters={'grade': 5}`

## Cost Management

### Typical costs
- Setup (indexing): $0.05 one-time
- Per query: $0.001-0.003
- 100 queries/day: ~$3/month
- 500 queries/day: ~$15/month

### Reduce costs
1. Use `gpt-4o-mini` (not `gpt-4o`)
2. Reduce `k` in advanced settings (fewer chunks retrieved)
3. Cache common queries (future feature)

## Updating Content

When you get new PDFs or curriculum updates:

```bash
# Delete old database
rm -rf chroma_db/

# Re-index
python indexer.py
```

## Getting Help

### Check these first:
1. README.md - Full documentation
2. ARCHITECTURE.md - Technical details
3. Error messages - Usually self-explanatory

### Common issues:

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"Error loading engine"**
```bash
# Make sure you indexed first
python indexer.py
```

**"Poor answer quality"**
- Try increasing k in advanced settings
- Use more specific questions
- Add filters (grade, curriculum)
- Check if content exists in your PDFs

## Next Steps

### Explore the modes
- Try all 4 modes: student, teacher, exam_prep, verse_lookup
- See how answers change

### Use filters effectively
- Filter by grade for grade-specific content
- Filter by curriculum to compare IPC vs Radiant Life
- Filter by doc_type to separate teacher/student materials

### Build something on top
- Export answers to PDF/Word
- Create a quiz generator
- Build a mobile app
- Add voice interface

## Pro Tips

1. **Better questions = better answers**
   - Specific: "What is Grade 5 Lesson 3 about?"
   - Not vague: "Tell me about lessons"

2. **Use the right mode**
   - Student mode: Simple explanations
   - Exam prep mode: Testable content
   - Verse lookup: Finding verses
   - Teacher mode: Teaching strategies

3. **Leverage filters**
   - Always filter by grade when asking grade-specific questions
   - Filter by curriculum when comparing materials

4. **Check sources**
   - Always review the source citations
   - Verify important information in the original PDFs

## Success Checklist

After setup, you should be able to:

- [ ] Ask a question and get an answer
- [ ] See source citations with lesson numbers
- [ ] Filter by grade/curriculum
- [ ] Switch between different modes
- [ ] Get memory verses accurately
- [ ] Use both web and CLI interfaces

## Share Your Feedback

This system is for the IPC ER Sunday School community. If you:
- Find bugs
- Have feature ideas
- Need help
- Want to contribute

Please reach out to the developer or church administration.

---

**Congratulations!** 🎉 You now have a personal AI assistant for IPC Sunday School curriculum!
