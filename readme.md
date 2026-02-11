# Mini-RAG: Local Document Retrieval System

A lightweight, locally running RAG (Retrieval-Augmented Generation) system that performs semantic search over PDF documents without requiring any external APIs or API keys.

## 🎯 Features

### Core Features(Must haves)

- ✅ **PDF Ingestion**: Loads and extracts text from multiple PDFs
- ✅ **Smart Chunking**: Breaks documents into overlapping chunks with sentence boundary awareness
- ✅ **Local Embeddings**: Uses sentence transformers for embedding generation
- ✅ **FAISS Indexing**: Fast similarity search with normalized cosine similarity
- ✅ **CLI Interface**: Simple command line interface for queries
- ✅ **Reproducible**: Complete setup with requirements.txt and pyproject.toml

### Bonus Features (Nice to haves)

- ✅ **JSON Output**: Export results as structured JSON
- ✅ **Streamlit UI**: Interactive web interface with real time search
- ✅ **Index Persistence**: Save and reload index from disk
- ✅ **Quality Assurance**: Pytest test suite with coverage
- ✅ **Code Quality**: Type hints, docstrings, and clean architecture

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone or download the repository**

```bash
cd mini-rag
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

Or using the modern approach with optional dependencies:

```bash
pip install -e .                    # Core only
pip install -e ".[ui]"              # With Streamlit UI
pip install -e ".[dev]"             # With development tools
pip install -e ".[ui,dev]"          # Everything
```

3. **Prepare your data**

Place your PDF files in the `./data/` directory:

```bash
mkdir -p data
```

**Don't have PDFs?** Generate sample files:

```bash
pip install reportlab
python create_sample_pdfs.py
```

This creates 5 sample PDFs about sensors in the `./data/` directory.

### Basic Usage

#### 1. Build the Index

```bash
python rag.py --build
```

This will:

- Load all PDFs from `./data/`
- Extract and chunk the text
- Generate embeddings using sentence transformers
- Build a FAISS index
- Save the index to `./index/`

#### 2. Query the System

```bash
python rag.py --query "Which sensors support 1200°C?"
```

Example output:

```
Loading index...
Loaded index with 47 chunks

Query: Which sensors support 1200°C?

================================================================================
SEARCH RESULTS
================================================================================

[Result 1]
Document: temperature_sensors
Page: 1
Score: 0.7823

Excerpt:
--------------------------------------------------------------------------------
Type K Thermocouples: - Operating range: -200°C to 1200°C - Accuracy: ±2.2°C
or ±0.75% - Applications: General purpose industrial measurements
--------------------------------------------------------------------------------

[Result 2]
Document: temperature_sensors
Page: 1
Score: 0.7156

Excerpt:
--------------------------------------------------------------------------------
Type N Thermocouples: - Operating range: -270°C to 1300°C - Accuracy: ±2.2°C
or ±0.75% - Better oxidation resistance than Type K
--------------------------------------------------------------------------------
...
```

#### 3. Save Results to JSON

```bash
python rag.py --query "pressure measurement" --json
```

Creates `results.json`:

```json
[
  {
    "doc_id": "pressure_sensors",
    "page": 1,
    "chunk_id": 5,
    "score": 0.8234,
    "text": "Strain Gauge Pressure Sensors: - Pressure range: 0 to 10,000 psi..."
  },
  ...
]
```

#### 4. Launch Streamlit UI

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

Features of the UI:

- 🔍 Interactive search with real time results
- 📊 Visual display of similarity scores
- 📄 Expandable result cards
- ⚙️ Configurable number of results
- 🔨 Index building from the UI

## 📁 Project Structure

```
mini-rag/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── document_processor.py   # PDF loading and chunking
│   ├── embeddings.py            # Embeddings and FAISS index
│   └── rag_engine.py            # Main RAG orchestration
├── tests/
│   ├── __init__.py
│   ├── test_document_processor.py
│   └── test_embeddings.py
│   └── test_rag_engine.py
├── data/                        # Place your PDFs here
├── index/                       # Generated index files (auto-created)
├── rag.py                       # CLI interface
├── app.py                       # Streamlit UI
├── config.py                    # Handle the configuration for RAG
├── create_sample_pdfs.py        # Generate sample PDFs
├── requirements.txt             # Dependencies
├── pyproject.toml               # Modern Python packaging
└── README.md                    # This file
```

## 🔧 Advanced Usage

### Custom Parameters

**Change chunk size and overlap:**

```python
from src.rag_engine import RAGEngine

rag = RAGEngine(
    data_dir="./data",
    chunk_size=800,      # Larger chunks
    overlap=100          # More overlap
)
rag.build_index()
```

**Retrieve more results:**

```bash
python rag.py --query "flow sensors" --top-k 5
```

**Use custom directories:**

```bash
python rag.py --build --data-dir ./my-pdfs --index-dir ./my-index
python rag.py --query "test" --index-dir ./my-index
```

### Programmatic Usage

```python
from src.rag_engine import RAGEngine

# Initialize
rag = RAGEngine(data_dir="./data")

# Build index (one-time)
rag.build_index()
rag.save_index("./index")

# Later: Load and query
rag.load_index("./index")
results = rag.query("Which sensors work at high temperatures?", top_k=3)

for result in results:
    print(f"Doc: {result['doc_id']}, Page: {result['page']}")
    print(f"Score: {result['score']}")
    print(f"Text: {result['text'][:200]}...")
```

## 🧪 Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=src --cov-report=html
```

Run Formatting check:

```bash
black --check src tests
```

## 🏗️ Design Decisions

### 1. **Chunking Strategy**

- **Chunk size**: 500 characters (configurable)
- **Overlap**: 50 characters (10%)
- **Rationale**: Balances context preservation with retrieval granularity
- **Enhancement**: Sentence boundary aware splitting to avoid mid sentence breaks

### 2. **Embedding Model**

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384
- **Rationale**:
  - Fast inference (~3-5ms per sentence)
  - Good semantic understanding
  - Runs locally on CPU
  - Small model size (~80MB)

### 3. **Similarity Search**

- **Index**: FAISS IndexFlatIP (Inner Product)
- **Metric**: Cosine similarity (via L2 normalization + inner product)
- **Rationale**: Exact search for small to medium datasets, easy to understand and debug

### 4. **Text Cleaning**

- Remove excessive whitespace
- Filter very short lines (headers/footers)
- Preserve paragraph structure
- **Future**: Could add more sophisticated header/footer detection

### 5. **Architecture**

- **Modular design**: Separate concerns (processing, embedding, indexing)
- **Type hints**: Full type annotation for better IDE support and error detection
- **Dataclasses**: Clean data structures with `Chunk` dataclass
- **Error handling**: Graceful degradation with informative messages

## ⏱️ Time Budget

**Total time spent**: ~4.0 hours

Breakdown:

- Core RAG implementation (document processing, embeddings, indexing): 2.0 hours
- CLI interface and JSON output: 0.5 hours
- Streamlit UI: 0.75 hours
- Testing and documentation: 0.5 hours
- Code quality (types, docstrings, refactoring): 0.25 hours

## 📋 To Do List (Future Improvements)

### Performance Optimizations

- [ ] Implement semantic caching for repeated queries
- [ ] Add batch processing for large PDF collections
- [ ] Use approximate nearest neighbor search (HNSW) for large scale deployment
- [ ] GPU acceleration for embedding generation

### Feature Enhancements

- [ ] Support for multiple file formats (Word, TXT, HTML)
- [ ] Metadata filtering (date range, document type, custom tags)
- [ ] Hybrid search (combine semantic + keyword/BM25)
- [ ] Query expansion and rewriting
- [ ] Multi query support (ask multiple questions at once)

### Quality Improvements

- [ ] Better header/footer detection using ML
- [ ] Image and figure extraction from PDFs
- [ ] OCR support for scanned documents
- [ ] Chunk quality metrics (coherence, completeness)

### User Experience

- [ ] Progress bars for all long operations
- [ ] PDF preview in Streamlit UI
- [ ] Export to Markdown/HTML reports
- [ ] Query history and favorites
- [ ] Multi user support with authentication
- [ ] API endpoint (FastAPI) for integration

### Robustness

- [ ] Graceful handling of corrupted PDFs
- [ ] Incremental index updates (add/remove documents)
- [ ] Index versioning and migration
- [ ] Comprehensive error recovery
- [ ] Logging and monitoring

## 🔍 Example Queries

With the sample PDFs, try these queries:

```bash
# Temperature-related
python rag.py --query "Which sensors support 1200°C?"
python rag.py --query "What is the accuracy of RTD sensors?"

# Pressure sensors
python rag.py --query "pressure measurement strain gauge"
python rag.py --query "What are piezoelectric sensors used for?"

# Flow measurement
python rag.py --query "magnetic flow meters conductive liquids"
python rag.py --query "non-invasive flow measurement"

# General
python rag.py --query "high temperature applications"
python rag.py --query "accuracy comparison"
```

## 🙏 Acknowledgments

- **sentence-transformers**: For easy to use embedding models
- **FAISS**: For efficient similarity search
- **Streamlit**: For rapid UI development
- **pdfplumber**: For reliable PDF text extraction

---

**Questions or issues?** This is a demonstration project showing local RAG implementation without API dependencies.
