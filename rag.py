#!/usr/bin/env python3
"""
Mini-RAG CLI interface.

Usage:
    python rag.py --build                                    # Build index from PDFs
    python rag.py --query "Which sensors support 1200°C?"   # Query the index
    python rag.py --query "..." --json                       # Save results to JSON
"""
import argparse
import sys
from pathlib import Path

from src.rag_engine import RAGEngine


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Mini-RAG: Local document retrieval without API keys",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build the index from PDFs in ./data/
  python rag.py --build

  # Query the index
  python rag.py --query "Which sensors support 1200°C?"

  # Query and save results to JSON
  python rag.py --query "temperature sensors" --json

  # Query with custom number of results
  python rag.py --query "pressure measurement" --top-k 5
        """
    )
    
    # Arguments
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build the index from PDFs in ./data/"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        help="Query string to search for"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of results to return (default: 3)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Save results to results.json"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data",
        help="Directory containing PDF files (default: ./data)"
    )
    
    parser.add_argument(
        "--index-dir",
        type=str,
        default="./index",
        help="Directory for index persistence (default: ./index)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.build and not args.query:
        parser.print_help()
        sys.exit(1)
    
    # Initialize RAG engine
    rag = RAGEngine(data_dir=args.data_dir)
    
    # Build index
    if args.build:
        print("Building RAG index...")
        rag.build_index()
        rag.save_index(args.index_dir)
        print(f"\nIndex saved to {args.index_dir}/")
        return
    
    # Query
    if args.query:
        # Check if index exists
        index_path = Path(args.index_dir)
        if not index_path.exists():
            print(f"Error: Index not found in {args.index_dir}/")
            print("Please run with --build first to create the index.")
            sys.exit(1)
        
        # Load index
        print("Loading index...")
        rag.load_index(args.index_dir)
        
        # Perform query
        print(f"\nQuery: {args.query}")
        results = rag.query(args.query, top_k=args.top_k)
        
        # Display results
        rag.print_results(results)
        
        # Save to JSON if requested
        if args.json:
            rag.save_results_json(results, "results.json")


if __name__ == "__main__":
    main()
