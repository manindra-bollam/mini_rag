"""
Integration tests for RAG engine.
"""

import json
import tempfile
from pathlib import Path

import pytest
from src.rag_engine import RAGEngine


class TestRAGEngineIntegration:
    """Integration tests for the full RAG pipeline."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_query_formatting(self) -> None:
        """Test query result formatting."""

        # Create a mock result
        mock_results = [
            {
                "doc_id": "test_doc",
                "page": 1,
                "chunk_id": 0,
                "score": 0.95,
                "text": "This is a test chunk of text.",
            }
        ]

        # Test JSON serialization
        json_str = json.dumps(mock_results)
        loaded = json.loads(json_str)

        assert len(loaded) == 1
        assert loaded[0]["doc_id"] == "test_doc"
        assert loaded[0]["score"] == 0.95

    def test_print_results_no_crash(self) -> None:
        """Test that print_results doesn't crash."""
        rag = RAGEngine()

        results = [
            {"doc_id": "doc1", "page": 1, "chunk_id": 0, "score": 0.9, "text": "Short text"},
            {
                "doc_id": "doc2",
                "page": 2,
                "chunk_id": 1,
                "score": 0.8,
                "text": "A" * 600,  # Long text to test truncation
            },
        ]

        # Should not raise any exception
        try:
            rag.print_results(results)
            assert True
        except Exception as e:
            pytest.fail(f"print_results raised exception: {e}")

    def test_save_load_results_json(self, temp_dir: Path) -> None:
        """Test saving and loading results as JSON."""
        rag = RAGEngine()

        results = [
            {
                "doc_id": "test",
                "page": 1,
                "chunk_id": 0,
                "score": 0.95,
                "text": "Test text with unicode: 你好 🔍",
            }
        ]

        json_path = temp_dir / "test_results.json"
        rag.save_results_json(results, str(json_path))

        # Verify file exists and is valid JSON
        assert json_path.exists()

        with open(json_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == results
        assert loaded[0]["text"] == "Test text with unicode: 你好 🔍"


class TestRAGEngineParameters:
    """Test RAG engine with different parameters."""

    def test_custom_chunk_size(self) -> None:
        """Test creating RAG engine with custom chunk size."""
        rag = RAGEngine(chunk_size=300, overlap=30)

        assert rag.chunker.chunk_size == 300
        assert rag.chunker.overlap == 30

    def test_custom_directories(self) -> None:
        """Test custom data and index directories."""
        rag = RAGEngine(data_dir="./custom_data")

        assert rag.data_dir == "./custom_data"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_query_with_empty_index(self) -> None:
        """Test querying before index is built."""
        rag = RAGEngine()

        # Should raise an error when querying without index
        with pytest.raises(ValueError):
            rag.query("test query")

    def test_load_nonexistent_index(self) -> None:
        """Test loading index that doesn't exist."""
        rag = RAGEngine()

        with pytest.raises(FileNotFoundError):
            rag.load_index("./nonexistent_index")
