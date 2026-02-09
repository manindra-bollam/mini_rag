"""
Embedding generation and FAISS indexing module.
"""
import pickle
from pathlib import Path
from typing import List, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .document_processor import Chunk


class EmbeddingEngine:
    """Handles text embedding generation using sentence-transformers."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding engine.
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        
    def load_model(self) -> None:
        """Load the embedding model."""
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print("Model loaded successfully")
        
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            
        Returns:
            NumPy array of embeddings
        """
        if self.model is None:
            self.load_model()
            
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        return embeddings


class FAISSIndex:
    """FAISS-based vector index for semantic search."""
    
    def __init__(self, dimension: int = 384):
        """
        Initialize FAISS index.
        
        Args:
            dimension: Dimension of embedding vectors (384 for MiniLM)
        """
        self.dimension = dimension
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[Chunk] = []
        
    def build_index(self, embeddings: np.ndarray, chunks: List[Chunk]) -> None:
        """
        Build FAISS index from embeddings.
        
        Args:
            embeddings: Array of embeddings
            chunks: List of corresponding chunks
        """
        # Normalize embeddings for cosine similarity using inner product
        faiss.normalize_L2(embeddings)
        
        # Create flat index with inner product (equivalent to cosine after normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings.astype('float32'))
        
        self.chunks = chunks
        
        print(f"Built FAISS index with {len(chunks)} chunks")
        
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[tuple]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (chunk, score) tuples
        """
        if self.index is None:
            raise ValueError("Index not built yet")
        
        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
                
        return results
    
    def save(self, index_path: str, chunks_path: str) -> None:
        """
        Save index and chunks to disk.
        
        Args:
            index_path: Path to save FAISS index
            chunks_path: Path to save chunks
        """
        if self.index is None:
            raise ValueError("No index to save")
            
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save chunks
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
            
        print(f"Index saved to {index_path}")
        print(f"Chunks saved to {chunks_path}")
        
    def load(self, index_path: str, chunks_path: str) -> None:
        """
        Load index and chunks from disk.
        
        Args:
            index_path: Path to FAISS index
            chunks_path: Path to chunks file
        """
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load chunks
        with open(chunks_path, 'rb') as f:
            self.chunks = pickle.load(f)
            
        print(f"Loaded index with {len(self.chunks)} chunks")
