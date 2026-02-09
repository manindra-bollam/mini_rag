# Mini-RAG Quick Reference

## Installation

```bash
pip install -r requirements.txt
```

## Common Commands

### Setup

```bash
# Generate sample PDFs
python create_sample_pdfs.py

# Build index
python rag.py --build
```

### Querying

```bash
# Basic query
python rag.py --query "Which sensors support 1200°C?"

# With JSON output
python rag.py --query "pressure sensors" --json

# Custom top-k
python rag.py --query "flow meters" --top-k 5
```

### UI

```bash
# Launch Streamlit
streamlit run app.py
```

### Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Run evaluation
python evaluate.py
```

### Development

```bash
# Format code
black src tests

# Lint
flake8 src tests

# Type check
mypy src
```

## Makefile Shortcuts

```bash
make install      # Install dependencies
make sample-data  # Generate sample PDFs
make build        # Build index
make query        # Run sample query
make ui           # Launch Streamlit
make test         # Run tests
make lint         # Run linters
make format       # Format code
```

## Directory Structure

```
data/          → Your PDF files
index/         → Generated FAISS index
results.json   → Query results (with --json)
```

## Python API

```python
from src.rag_engine import RAGEngine

# Create engine
rag = RAGEngine(data_dir="./data")

# Build index
rag.build_index()
rag.save_index("./index")

# Query
results = rag.query("your query", top_k=3)

# Load existing index
rag.load_index("./index")
```

## Configuration

Edit `config.py` to customize:

- Chunk size and overlap
- Embedding model
- Default top-k
- Batch size

## Troubleshooting

**Index not found**

```bash
python rag.py --build
```

**No PDFs found**

```bash
# Add PDFs to data/ or generate samples
python create_sample_pdfs.py
```

**Import errors**

```bash
pip install -r requirements.txt
```

## Example Queries (with sample data)

```bash
python rag.py --query "Which sensors support 1200°C?"
python rag.py --query "What is the accuracy of RTD sensors?"
python rag.py --query "pressure measurement strain gauge"
python rag.py --query "non-invasive flow measurement"
python rag.py --query "humidity sensors temperature range"
```
