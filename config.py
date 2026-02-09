"""
Configuration file for Mini-RAG.

Modify these settings to customize the RAG system behavior.
"""

# Data settings
DATA_DIR = "./data"
INDEX_DIR = "./index"

# Chunking settings
CHUNK_SIZE = 500  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks (characters)

# Embedding settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # Dimension for MiniLM model
BATCH_SIZE = 32  # Batch size for embedding generation

# Search settings
DEFAULT_TOP_K = 3  # Default number of results to return
MAX_TOP_K = 20  # Maximum allowed top-k

# Display settings
MAX_EXCERPT_LENGTH = 500  # Maximum length for text excerpts in display

# Performance settings
USE_GPU = False  # Set to True if you have a CUDA-enabled GPU

# Index settings
INDEX_TYPE = "flat"  # Options: "flat" (exact), "ivf" (approximate)
SAVE_INDEX_ON_BUILD = True  # Automatically save index after building