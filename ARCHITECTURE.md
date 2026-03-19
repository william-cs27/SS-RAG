# IPC Sunday School RAG - Technical Architecture

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     INDEXING PHASE (One-time)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌───────────────────────────────────────────────────┐
    │  PDF Files (IPC, Radiant Life, Christian Identity) │
    └──────────────────────┬────────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │         PDF Parser (PyMuPDF)                      │
    │  • Extract text page-by-page                      │
    │  • Detect lesson boundaries                        │
    │  • Extract memory verses                           │
    │  • Extract metadata from filename                  │
    └──────────────────────┬───────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │         Smart Chunking                            │
    │  • Chunk by lesson when possible                  │
    │  • 600 char chunks with 100 char overlap          │
    │  • Preserve metadata per chunk                    │
    └──────────────────────┬───────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │    Embedding Generation                           │
    │  Model: models/embedding-001 (Google)              │
    │  Dimensions: 768                                   │
    └──────────────────────┬───────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │    ChromaDB Vector Store                          │
    │  • Local storage (chroma_db/)                     │
    │  • Persistent                                     │
    │  • Metadata filtering support                     │
    └──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  QUERY PHASE (Every request)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌──────────────────────────────────────────────────┐
    │  User Query + Filters                             │
    │  Example: "What is Grade 5 Lesson 3 about?"      │
    │  Filters: {grade: 5, curriculum: "IPC"}          │
    └──────────────────────┬───────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │  Query Embedding                                  │
    │  Same model: models/embedding-001                  │
    └──────────────────────┬───────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │  Vector Similarity Search                         │
    │  • Find top-k most similar chunks                 │
    │  • Apply metadata filters                         │
    │  • Default k=5, adjustable                        │
    └──────────────────────┬───────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │  Context Assembly                                 │
    │  Retrieved chunks + metadata → prompt context     │
    └──────────────────────┬───────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │  LLM Generation                                   │
    │  Model: gemini-2.0-flash                          │
    │  Temperature: 0.3 (factual)                       │
    │  Mode-specific prompt templates                   │
    └──────────────────────┬───────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │  Response + Sources                               │
    │  • Answer based on retrieved context              │
    │  • Citations with metadata                        │
    │  • Source document references                     │
    └───────────────────────────────────────────────────┘
```

## Model Specifications

### Embedding Model: models/embedding-001 (Google)

**Why chosen:**
- Excellent quality from Google's embedding models
- Strong performance on educational/religious text
- API-based = no local GPU needed
- Fast inference (<100ms per query)

**Specifications:**
- Dimensions: 768
- Provider: Google Generative AI

**Performance on IPC content:**
- Excellent semantic understanding of biblical terms
- Good at distinguishing between similar concepts
- Handles grade-level content variation well

### LLM: gemini-2.0-flash (Google)

**Why chosen:**
- Excellent instruction following
- Strong at staying grounded in retrieved context
- Fast response time (1-2 seconds)
- Good at handling educational content

**Specifications:**
- Context window: 1M tokens
- Temperature: 0.3 (set for factual responses)

**Performance characteristics:**
- Hallucination rate: Very low with RAG context
- Citation accuracy: Excellent
- Grounding: Strong tendency to stick to provided context
- Tone adaptation: Good at matching mode (student/teacher)

**Alternatives:**
1. `gemini-2.0-pro`
   - Better reasoning, but unnecessary for RAG
   - Verdict: Overkill for this use case

### Vector Database: ChromaDB

**Why chosen:**
- Easy setup (single pip install)
- Local-first (no cloud dependency)
- Excellent metadata filtering
- Persistent storage
- Perfect for <100K documents

**Specifications:**
- Storage: SQLite + DuckDB backend
- Embeddings: Stored as float32 arrays
- Metadata: JSON indexing
- Distance metric: Cosine similarity

**Query performance:**
- 5K vectors: <10ms
- 50K vectors: <50ms
- 500K vectors: <200ms

**Alternatives considered:**
1. **Pinecone** (cloud)
   - Pros: Managed, scalable, fast
   - Cons: $70/month minimum, overkill for this
   - Verdict: Unnecessary complexity

2. **FAISS** (local)
   - Pros: Fastest for large scale
   - Cons: No metadata filtering, more complex
   - Verdict: Overkill for <10K documents

3. **Weaviate** (self-hosted/cloud)
   - Pros: Feature-rich, scalable
   - Cons: More complex setup
   - Verdict: Unnecessary for this scale

## Chunking Strategy

### Lesson-Based Chunking (Primary)

```python
# Detect lesson boundaries
Lesson 1: The Creation → Chunk 1 (500 chars)
Lesson 2: Adam and Eve → Chunk 2 (750 chars)
                      → Chunk 2a (600 chars, overflow)
```

**Advantages:**
- Preserves semantic units (full lessons)
- Natural alignment with curriculum structure
- Easier citation ("from Lesson 5")
- Better for exam prep (lessons are test units)

**Implementation:**
- Regex pattern matching for "Lesson X: Title"
- Extract memory verses per lesson
- Split long lessons into sub-chunks
- Preserve lesson metadata on all sub-chunks

### Fallback: Fixed-Size Chunking

When lesson detection fails:
- Chunk size: 600 characters
- Overlap: 100 characters
- Boundary: Prefer sentence endings

**Why 600 chars?**
- ~150 tokens (3-4 sentences)
- Fits one concept typically
- Not too small (context preserved)
- Not too large (retrieval precision)

### Metadata Attached Per Chunk

```python
{
    'curriculum': 'IPC' | 'Radiant Life' | 'Christian Identity',
    'grade': 1-13,
    'doc_type': 'textbook' | 'teacher_guide' | 'student_guide',
    'lesson_number': 1-20,
    'lesson_title': 'The Creation',
    'page_number': 42,
    'exam_relevant': True | False,
    'contains_verse': True | False,
    'source_file': 'IPC_Grade_5.pdf'
}
```

## Query Modes & Prompt Engineering

### Student Mode

**Prompt characteristics:**
- Simple language
- Clear explanations
- Complete verse quotations
- Grade-appropriate tone
- Acknowledges gaps in knowledge

**Example prompt:**
```
You are a helpful Sunday School teaching assistant. 
Answer the student's question based ONLY on the provided 
context from the IPC curriculum textbooks.

Instructions:
- Give a clear, easy-to-understand answer
- Use the exact content from the textbooks
- If the answer includes a Bible verse, quote it fully
...
```

### Teacher Mode

**Prompt characteristics:**
- Professional tone
- Teaching strategies included
- Cross-references suggested
- Comprehensive coverage
- Practical tips emphasized

### Exam Prep Mode

**Prompt characteristics:**
- Focus on testable content
- Break down into key points
- Include practice questions
- Emphasize memory verses
- Citation of grade/lesson

### Verse Lookup Mode

**Prompt characteristics:**
- Exact verse reproduction
- Bible reference included
- Multiple matches shown
- Lesson context provided

## Performance Metrics

### Indexing (25 PDFs, ~5,000 pages)

| Metric | Value |
|--------|-------|
| Parse time | 2-5 minutes |
| Embedding time | 5-10 minutes |
| Total chunks | ~2,500-5,000 |
| Database size | ~50-100 MB |
| Cost | ~$0.05 |

### Query Performance (per request)

| Metric | Value |
|--------|-------|
| Query embedding | 50-100ms |
| Vector search | 10-50ms |
| LLM generation | 1-2 seconds |
| Total latency | 1.5-2.5 seconds |
| Cost per query | $0.001-0.003 |

### Scale Estimates

| Users | Queries/day | Monthly cost | DB size |
|-------|------------|--------------|---------|
| 10 | 50 | $0.15 | 50 MB |
| 100 | 500 | $1.50 | 50 MB |
| 1,000 | 5,000 | $15 | 50 MB |

**Note:** Database size doesn't grow with users, only with content.

## Deployment Options

### Option 1: Local Laptop (Recommended for personal use)

**Requirements:**
- 8GB RAM minimum
- 10GB disk space
- Internet connection (for API calls)

**Cost:** ~$1-2/month for API usage

**Setup time:** 15 minutes

### Option 2: Local Server (For church/school)

**Requirements:**
- Server with 16GB RAM
- 50GB disk space
- Dedicated IP/domain
- SSL certificate

**Cost:** 
- Hardware: One-time
- API: ~$5-20/month depending on usage

**Advantages:**
- Multiple concurrent users
- Always available
- No laptop dependency

### Option 3: Cloud Deployment (For large scale)

**Stack:**
- AWS EC2 / Google Cloud VM
- Docker container
- Managed vector DB (optional)
- Load balancer (if needed)

**Cost estimate:**
- VM: $20-50/month
- API: $10-100/month
- Storage: $5/month

**Advantages:**
- Scales to thousands of users
- Professional reliability
- Backup/redundancy

## Security Considerations

### Data Privacy

1. **Local storage** - Vector DB is local, no cloud upload
2. **API calls** - Only embeddings and prompts sent to Google
3. **Deletion** - Delete `chroma_db/` to remove all indexed data

### API Key Security

```bash
# .env file (never commit to git)
GOOGLE_API_KEY=your-key-here

# .gitignore includes:
.env
chroma_db/
```

### User Authentication (if deploying as service)

For multi-user deployment, consider:
- User login system
- Query logging per user
- Rate limiting per user
- Access control by grade/role

## Optimization Techniques

### Hybrid Search (Future Enhancement)

Combine dense + sparse retrieval:
```python
# Dense: Vector similarity (current)
# Sparse: BM25 keyword matching (add this)
# Hybrid: Weighted combination

final_results = 0.7 * vector_results + 0.3 * bm25_results
```

**Expected improvement:** 10-15% better precision

### Re-ranking (Future Enhancement)

After retrieving top-10 chunks:
1. Use cross-encoder to re-score
2. Take top-5 for LLM context

**Expected improvement:** 15-20% better relevance

### Caching (Future Enhancement)

Cache common queries:
```python
cache = {
    "What is Grade 5 Lesson 3 about?": {
        'answer': "...",
        'timestamp': "...",
        'ttl': 86400  # 24 hours
    }
}
```

**Expected improvement:** 
- 99% faster for cached queries
- 90% cost reduction for common queries

## Maintenance

### Regular Tasks

1. **Re-index when content changes**
   ```bash
   rm -rf chroma_db/
   python indexer.py
   ```

2. **Monitor API usage**
   - Check Google AI Studio dashboard
   - Set billing alerts if applicable

3. **Backup database**
   ```bash
   tar -czf chroma_backup.tar.gz chroma_db/
   ```

### Troubleshooting

**Slow queries?**
- Reduce k (fewer chunks retrieved)
- Check internet connection
- Verify API quota not exceeded

**Poor answers?**
- Check if content exists in PDFs
- Increase k (more context)
- Try different query phrasing
- Check metadata filters

**High costs?**
- Review number of queries
- Check k value (lower = cheaper)
- Consider caching common queries

## Future Roadmap

### Phase 1 (Current)
- ✅ Basic RAG implementation
- ✅ 4 query modes
- ✅ Metadata filtering
- ✅ Web + CLI interfaces

### Phase 2 (Next 3 months)
- [ ] Hybrid search
- [ ] Query caching
- [ ] Malayalam language support
- [ ] Export to PDF/Word

### Phase 3 (Next 6 months)
- [ ] Auto-quiz generator
- [ ] Progress tracking
- [ ] Mobile app
- [ ] Offline mode with local LLM (e.g., Ollama)

### Phase 4 (Long-term)
- [ ] Multi-church deployment
- [ ] Federated learning
- [ ] Voice interface
- [ ] AR study features
