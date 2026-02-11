"""
PDF document processing and chunking module.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pdfplumber


@dataclass
class Chunk:
    """Represents a text chunk from a document."""

    doc_id: str
    page: int
    chunk_id: int
    text: str

    def to_dict(self) -> dict:
        """Convert chunk to dictionary."""
        return {
            "doc_id": self.doc_id,
            "page": self.page,
            "chunk_id": self.chunk_id,
            "text": self.text,
        }


class DocumentProcessor:
    """Handles PDF loading and text extraction."""

    def __init__(self, data_dir: str = "./data"):
        """
        Initialize document processor.

        Args:
            data_dir: Directory containing PDF files
        """
        self.data_dir = Path(data_dir)

    def load_pdfs(self) -> List[tuple]:
        """
        Load all PDF files from data directory.

        Returns:
            List of tuples (doc_id, extracted_text_per_page)
        """
        pdf_files = list(self.data_dir.glob("*.pdf"))

        if not pdf_files:
            raise ValueError(f"No PDF files found in {self.data_dir}")

        documents = []

        for pdf_path in sorted(pdf_files):
            doc_id = pdf_path.stem
            pages_text = self._extract_text(pdf_path)
            documents.append((doc_id, pages_text))

        return documents

    def _extract_text(self, pdf_path: Path) -> List[str]:
        """
        Extract text from PDF with robust handling.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of text strings, one per page
        """
        pages_text = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    # Clean the text
                    text = self._clean_text(text)
                    pages_text.append(text)
        except Exception as e:
            print(f"Warning: Error processing {pdf_path}: {e}")

        return pages_text

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing artifacts.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove common page artifacts (page numbers, headers/footers patterns)
        # Simple heuristic: remove lines that are very short at start/end
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Keep lines that have substantial content
            if len(line) > 10 or any(c.isalpha() for c in line):
                cleaned_lines.append(line)

        text = " ".join(cleaned_lines)
        text = text.strip()

        return text


class TextChunker:
    """Handles text chunking with overlap."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize text chunker.

        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_documents(self, documents: List[tuple]) -> List[Chunk]:
        """
        Chunk all documents into overlapping text segments.

        Args:
            documents: List of (doc_id, pages_text) tuples

        Returns:
            List of Chunk objects
        """
        all_chunks = []

        for doc_id, pages_text in documents:
            for page_num, page_text in enumerate(pages_text, start=1):
                if not page_text.strip():
                    continue

                page_chunks = self._chunk_text(page_text)

                for chunk_idx, chunk_text in enumerate(page_chunks):
                    chunk = Chunk(
                        doc_id=doc_id, page=page_num, chunk_id=len(all_chunks), text=chunk_text
                    )
                    all_chunks.append(chunk)

        return all_chunks

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the boundary
                boundary_text = text[max(0, end - 100): min(len(text), end + 100)]
                sentence_ends = [m.end() for m in re.finditer(r"[.!?]\s+", boundary_text)]

                if sentence_ends:
                    # Find closest sentence end to our target
                    target_pos = min(100, len(boundary_text))
                    closest = min(sentence_ends, key=lambda x: abs(x - target_pos))
                    end = max(0, end - 100) + closest

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = end - self.overlap

            # Avoid infinite loop
            if start >= len(text) - self.overlap:
                break

        return chunks
