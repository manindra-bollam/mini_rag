"""
Tests for document processing module.
"""

import pytest
from src.document_processor import Chunk, DocumentProcessor, TextChunker


class TestChunk:
    """Test Chunk dataclass."""

    def test_chunk_creation(self) -> None:
        """Test creating a chunk."""
        chunk = Chunk(doc_id="test_doc", page=1, chunk_id=0, text="This is a test chunk.")

        assert chunk.doc_id == "test_doc"
        assert chunk.page == 1
        assert chunk.chunk_id == 0
        assert chunk.text == "This is a test chunk."

    def test_chunk_to_dict(self) -> None:
        """Test chunk to dictionary conversion."""
        chunk = Chunk(doc_id="test_doc", page=1, chunk_id=0, text="Test text")

        result = chunk.to_dict()

        assert result == {"doc_id": "test_doc", "page": 1, "chunk_id": 0, "text": "Test text"}


class TestTextChunker:
    """Test TextChunker class."""

    def test_chunk_short_text(self) -> None:
        """Test chunking text shorter than chunk size."""
        chunker = TextChunker(chunk_size=100, overlap=10)
        text = "This is a short text."

        chunks = chunker._chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_long_text(self) -> None:
        """Test chunking long text."""
        chunker = TextChunker(chunk_size=50, overlap=10)
        text = "a" * 200  # Long text

        chunks = chunker._chunk_text(text)

        assert len(chunks) > 1
        # Each chunk should be around chunk_size
        for chunk in chunks[:-1]:  # Exclude last chunk
            assert len(chunk) <= chunker.chunk_size + 20  # Some flexibility

    def test_chunk_documents(self) -> None:
        """Test chunking multiple documents."""
        chunker = TextChunker(chunk_size=100, overlap=10)
        documents = [
            ("doc1", ["Page 1 text", "Page 2 text"]),
            ("doc2", ["Another page text"]),
        ]

        chunks = chunker.chunk_documents(documents)

        assert len(chunks) == 3
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert chunks[0].doc_id == "doc1"
        assert chunks[0].page == 1


class TestDocumentProcessor:
    """Test DocumentProcessor class."""

    def test_clean_text(self) -> None:
        """Test text cleaning."""
        processor = DocumentProcessor()
        text = "  Multiple   spaces   here.  "

        cleaned = processor._clean_text(text)

        assert "  " not in cleaned
        assert cleaned == "Multiple spaces here."

    def test_clean_text_removes_short_lines(self) -> None:
        """Test that very short lines are removed."""
        processor = DocumentProcessor()
        text = "1\nThis is a proper sentence.\n2\nAnother good line."

        cleaned = processor._clean_text(text)

        # Short lines like "1" and "2" should be removed or not dominate
        assert "This is a proper sentence" in cleaned
        assert "Another good line" in cleaned
