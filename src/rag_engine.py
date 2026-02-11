"""
Main RAG engine that orchestrates document processing, embedding, and querying.
"""

import json
from pathlib import Path
from typing import List

from .document_processor import Chunk, DocumentProcessor, TextChunker
from .embeddings import EmbeddingEngine, FAISSIndex


class RAGEngine:
    """Main RAG engine for document retrieval."""

    def __init__(
        self,
        data_dir: str = "./data",
        chunk_size: int = 500,
        overlap: int = 50,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """
        Initialize RAG engine.

        Args:
            data_dir: Directory containing PDF files
            chunk_size: Size of text chunks in characters
            overlap: Overlap between chunks in characters
            model_name: Name of embedding model
        """
        self.data_dir = data_dir
        self.doc_processor = DocumentProcessor(data_dir)
        self.chunker = TextChunker(chunk_size, overlap)
        self.embedding_engine = EmbeddingEngine(model_name)
        self.index = FAISSIndex(dimension=384)
        self.chunks: List[Chunk] = []

    def build_index(self) -> None:
        """Build the RAG index from PDFs in data directory."""
        print("=" * 50)
        print("Building RAG Index")
        print("=" * 50)

        # Load PDFs
        print("\n1. Loading PDFs...")
        documents = self.doc_processor.load_pdfs()
        print(f"Loaded {len(documents)} documents")

        # Chunk documents
        print("\n2. Chunking documents...")
        self.chunks = self.chunker.chunk_documents(documents)
        print(f"Created {len(self.chunks)} chunks")

        # Generate embeddings
        print("\n3. Generating embeddings...")
        texts = [chunk.text for chunk in self.chunks]
        embeddings = self.embedding_engine.embed_texts(texts)
        print(f"Generated {len(embeddings)} embeddings")

        # Build FAISS index
        print("\n4. Building FAISS index...")
        self.index.build_index(embeddings, self.chunks)

        print("\n" + "=" * 50)
        print("Index built successfully!")
        print("=" * 50)

    def query(self, query_text: str, top_k: int = 3) -> List[dict]:
        """
        Query the RAG system.

        Args:
            query_text: Query string
            top_k: Number of results to return

        Returns:
            List of result dictionaries
        """
        # Generate query embedding
        query_embedding = self.embedding_engine.embed_texts([query_text])[0]

        # Search index
        results = self.index.search(query_embedding, top_k)

        # Format results
        formatted_results = []
        for chunk, score in results:
            result = {
                "doc_id": chunk.doc_id,
                "page": chunk.page,
                "chunk_id": chunk.chunk_id,
                "score": round(score, 4),
                "text": chunk.text,
            }
            formatted_results.append(result)

        return formatted_results

    def save_index(self, index_dir: str = "./index") -> None:
        """
        Save index to disk.

        Args:
            index_dir: Directory to save index files
        """
        index_path = Path(index_dir)
        index_path.mkdir(exist_ok=True)

        faiss_path = str(index_path / "faiss.index")
        chunks_path = str(index_path / "chunks.pkl")

        self.index.save(faiss_path, chunks_path)

    def load_index(self, index_dir: str = "./index") -> None:
        """
        Load index from disk.

        Args:
            index_dir: Directory containing index files
        """
        index_path = Path(index_dir)

        faiss_path = str(index_path / "faiss.index")
        chunks_path = str(index_path / "chunks.pkl")

        if not Path(faiss_path).exists() or not Path(chunks_path).exists():
            raise FileNotFoundError(
                f"Index files not found in {index_dir}. Please build the index first."
            )

        self.index.load(faiss_path, chunks_path)
        self.chunks = self.index.chunks

        # Load embedding model (needed for queries)
        self.embedding_engine.load_model()

    def print_results(self, results: List[dict]) -> None:
        """
        Print query results in a formatted way.

        Args:
            results: List of result dictionaries
        """
        print("\n" + "=" * 80)
        print("SEARCH RESULTS")
        print("=" * 80)

        for i, result in enumerate(results, 1):
            print(f"\n[Result {i}]")
            print(f"Document: {result['doc_id']}")
            print(f"Page: {result['page']}")
            print(f"Score: {result['score']:.4f}")
            print(f"\nExcerpt:")
            print("-" * 80)
            # Truncate very long text for display
            text = result["text"]
            if len(text) > 500:
                text = text[:500] + "..."
            print(text)
            print("-" * 80)

    def save_results_json(self, results: List[dict], output_path: str = "results.json") -> None:
        """
        Save results to JSON file.

        Args:
            results: List of result dictionaries
            output_path: Path to output JSON file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to {output_path}")
