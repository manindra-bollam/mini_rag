"""
Tests for embeddings module.
"""
import numpy as np
import pytest
from src.document_processor import Chunk
from src.embeddings import EmbeddingEngine, FAISSIndex


class TestEmbeddingEngine:
    """Test EmbeddingEngine class."""
    
    def test_embed_texts(self) -> None:
        """Test embedding generation."""
        engine = EmbeddingEngine()
        texts = ["This is a test.", "Another test sentence."]
        
        embeddings = engine.embed_texts(texts)
        
        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] == 384  # MiniLM dimension
        assert embeddings.dtype == np.float32 or embeddings.dtype == np.float64
    
    def test_embedding_similarity(self) -> None:
        """Test that similar texts have similar embeddings."""
        engine = EmbeddingEngine()
        texts = [
            "The cat sat on the mat.",
            "A feline rested on the rug.",  # Similar meaning
            "Quantum physics is complex."   # Different meaning
        ]
        
        embeddings = engine.embed_texts(texts)
        
        # Compute cosine similarity
        def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        sim_0_1 = cosine_similarity(embeddings[0], embeddings[1])
        sim_0_2 = cosine_similarity(embeddings[0], embeddings[2])
        
        # Similar sentences should be more similar than dissimilar ones
        assert sim_0_1 > sim_0_2


class TestFAISSIndex:
    """Test FAISSIndex class."""
    
    def test_build_and_search(self) -> None:
        """Test building index and searching."""
        # Create sample data
        chunks = [
            Chunk(doc_id="doc1", page=1, chunk_id=0, text="Temperature sensor"),
            Chunk(doc_id="doc1", page=2, chunk_id=1, text="Pressure measurement"),
            Chunk(doc_id="doc2", page=1, chunk_id=2, text="Heat detection"),
        ]
        
        # Generate embeddings
        engine = EmbeddingEngine()
        texts = [c.text for c in chunks]
        embeddings = engine.embed_texts(texts)
        
        # Build index
        index = FAISSIndex(dimension=384)
        index.build_index(embeddings, chunks)
        
        # Search
        query = "temperature"
        query_embedding = engine.embed_texts([query])[0]
        results = index.search(query_embedding, top_k=2)
        
        assert len(results) == 2
        assert all(isinstance(r[0], Chunk) for r in results)
        assert all(isinstance(r[1], float) for r in results)
        
        # First result should be temperature-related
        assert "temperature" in results[0][0].text.lower() or "heat" in results[0][0].text.lower()
    
    def test_search_returns_top_k(self) -> None:
        """Test that search returns correct number of results."""
        chunks = [Chunk(doc_id=f"doc{i}", page=1, chunk_id=i, text=f"Text {i}") 
                  for i in range(10)]
        
        engine = EmbeddingEngine()
        texts = [c.text for c in chunks]
        embeddings = engine.embed_texts(texts)
        
        index = FAISSIndex(dimension=384)
        index.build_index(embeddings, chunks)
        
        query_embedding = engine.embed_texts(["test query"])[0]
        
        for k in [1, 3, 5]:
            results = index.search(query_embedding, top_k=k)
            assert len(results) == k