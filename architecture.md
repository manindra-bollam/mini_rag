# Mini-RAG Architecture

## Overview

Mini-RAG is a locally-running retrieval-augmented generation (RAG) system designed to perform semantic search over PDF documents without requiring external APIs or API keys. The system is built with modularity, testability, and extensibility in mind.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  CLI (rag.py)│  │ Streamlit UI │  │  Python API  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────┐
│                    RAG Engine Layer                           │
│                    ┌────────────────┐                         │
│                    │   RAGEngine    │                         │
│                    └────────┬───────┘                         │
│                             │                                 │
│          ┌──────────────────┼──────────────────┐             │
│          │                  │                  │              │
│  ┌───────▼───────┐  ┌──────▼──────┐  ┌───────▼────────┐    │
│  │   Document    │  │  Embedding  │  │  FAISS Index   │    │
│  │   Processor   │  │   Engine    │  │                │    │
│  └───────────────┘  └─────────────┘  └────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────┐
│                    Storage Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  PDF Files   │  │ FAISS Index  │  │    Chunks    │       │
│  │  (./data/)   │  │ (./index/)   │  │  (pickle)    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Document Processor (`document_processor.py`)

**Responsibility**: Load PDFs and chunk text into retrievable segments.

**Key Classes**:

- `DocumentProcessor`: Handles PDF loading and text extraction
- `TextChunker`: Splits documents into overlapping chunks
- `Chunk`: Data class representing a text chunk

**Flow**:

1. Scan `./data/` directory for PDF files
2. Extract text using pdfplumber
3. Clean text (remove artifacts, normalize whitespace)
4. Split into overlapping chunks with sentence-boundary awareness
5. Return list of `Chunk` objects with metadata

**Design Decisions**:

- Used pdfplumber over PyPDF2 for better table/layout handling
- Implemented overlap to preserve context across chunk boundaries
- Sentence-aware splitting to avoid mid-sentence breaks
- Configurable chunk size (default: 500 chars)

### 2. Embedding Engine (`embeddings.py`)

**Responsibility**: Generate vector embeddings and build searchable index.

**Key Classes**:

- `EmbeddingEngine`: Generates embeddings using sentence-transformers
- `FAISSIndex`: Manages FAISS vector index

**Flow**:

1. Load sentence-transformer model (`all-MiniLM-L6-v2`)
2. Generate embeddings for all chunks (batch processing)
3. Normalize embeddings for cosine similarity
4. Build FAISS flat index with inner product metric
5. Store chunks alongside index for retrieval

**Design Decisions**:

- Used sentence-transformers for ease of use and quality
- Chose `all-MiniLM-L6-v2` for balance of speed/quality/size
- L2 normalization + inner product = cosine similarity
- Flat index (exact search) suitable for small-to-medium datasets
- Can be extended to IVF/HNSW for larger datasets

### 3. RAG Engine (`rag_engine.py`)

**Responsibility**: Orchestrate the entire RAG pipeline.

**Key Class**: `RAGEngine`

**Methods**:

- `build_index()`: Build index from PDFs
- `query()`: Perform semantic search
- `save_index()` / `load_index()`: Persist/restore index
- `print_results()`: Format and display results
- `save_results_json()`: Export results to JSON

**Flow**:

```
build_index():
  └─> Load PDFs (DocumentProcessor)
  └─> Chunk documents (TextChunker)
  └─> Generate embeddings (EmbeddingEngine)
  └─> Build FAISS index (FAISSIndex)
  └─> Save to disk

query():
  └─> Generate query embedding (EmbeddingEngine)
  └─> Search index (FAISSIndex)
  └─> Format and return results
```

## Data Flow

### Index Building

```
PDF Files → Extract Text → Clean Text → Chunk Text →
Generate Embeddings → Build FAISS Index → Save to Disk
```

### Querying

```
User Query → Generate Embedding → Search FAISS Index →
Retrieve Chunks → Format Results → Return to User
```

## File Structure

```
mini-rag/
├── src/                         # Core library
│   ├── document_processor.py   # PDF loading and chunking
│   ├── embeddings.py            # Embeddings and FAISS
│   └── rag_engine.py            # Main orchestrator
├── tests/                       # Test suite
│   ├── test_document_processor.py
│   ├── test_embeddings.py
│   └── test_rag_engine.py
├── data/                        # Input PDFs
├── index/                       # Persisted index
├── rag.py                       # CLI interface
├── app.py                       # Streamlit UI
├── evaluate.py                  # Evaluation tools
├── examples.py                  # Usage examples
└── config.py                    # Configuration
```

## Performance Characteristics

### Time Complexity

- **Index Building**: O(n × d) where n = number of chunks, d = embedding dimension
- **Query**: O(n × d) for flat index (exact search)
- **With IVF index**: O(√n × d) (approximate)

### Space Complexity

- **Embeddings**: n × d × 4 bytes (float32)
- **Chunks**: Variable (depends on text)
- **Total**: ~10-50MB for 100 PDFs

### Typical Performance

- Index building: ~1-2 minutes for 100 PDFs
- Query latency: ~50-100ms (CPU)
- Embedding generation: ~3-5ms per chunk (CPU)

## Scalability Considerations

### Current Limits

- Designed for: 10-1000 PDFs
- Chunk count: Up to 100,000 chunks
- Index type: Flat (exact search)

### Scaling Strategies

1. **For 1K-10K PDFs**:
   - Use IVF index (IndexIVFFlat)
   - Increase batch size for embeddings
   - Consider multi-threading

2. **For 10K+ PDFs**:
   - Use HNSW index (faster approximate search)
   - Implement chunked index building
   - Consider distributed storage
   - GPU acceleration for embeddings

3. **For Real-Time Applications**:
   - Pre-compute and cache embeddings
   - Use approximate indices (HNSW, IVF)
   - Implement result caching
   - Load index into memory

## Extension Points

### Adding New Document Types

```python
# Extend DocumentProcessor
class DocumentProcessor:
    def _extract_text(self, file_path: Path) -> List[str]:
        if file_path.suffix == '.pdf':
            return self._extract_pdf(file_path)
        elif file_path.suffix == '.docx':
            return self._extract_docx(file_path)
        # Add more types...
```

### Custom Embedding Models

```python
# Change model in config.py or pass to RAGEngine
rag = RAGEngine(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

### Hybrid Search (Keyword + Semantic)

```python
# Combine BM25 and vector search
from rank_bm25 import BM25Okapi

class HybridIndex:
    def __init__(self):
        self.faiss_index = FAISSIndex()
        self.bm25 = BM25Okapi(corpus)

    def search(self, query, alpha=0.5):
        semantic_scores = self.faiss_index.search(query)
        keyword_scores = self.bm25.get_scores(query)
        return alpha * semantic_scores + (1-alpha) * keyword_scores
```

### Metadata Filtering

```python
# Add metadata to chunks
@dataclass
class Chunk:
    doc_id: str
    page: int
    chunk_id: int
    text: str
    metadata: Dict[str, Any]  # Add metadata

# Filter before returning
def query_with_filter(query, filters):
    results = self.index.search(query, top_k=100)
    filtered = [r for r in results if matches_filters(r, filters)]
    return filtered[:top_k]
```

## Testing Strategy

### Unit Tests

- Test each component in isolation
- Mock dependencies
- Focus on edge cases

### Integration Tests

- Test full pipeline
- Use small sample data
- Verify end-to-end flow

### Evaluation Tests

- Keyword recall metrics
- Manual query evaluation
- Benchmark against ground truth

## Security Considerations

1. **File Safety**: Validate PDF files before processing
2. **Input Sanitization**: Clean user queries
3. **Path Traversal**: Restrict file access to designated directories
4. **Resource Limits**: Prevent DoS via large files or queries
5. **Data Privacy**: All processing is local (no external API calls)

## Future Enhancements

See the "To-Do List" section in README.md for a comprehensive list of planned improvements.

## References

- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [RAG Papers](https://arxiv.org/abs/2005.11401)
