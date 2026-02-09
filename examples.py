"""
Example Usage of Mini-RAG

This script demonstrates various ways to use the Mini-RAG system.
"""
from pathlib import Path
from src.rag_engine import RAGEngine
from evaluate import RAGEvaluator, SENSOR_TEST_CASES


def example_1_basic_usage():
    """Example 1: Basic RAG workflow."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 80)
    
    # Initialize RAG engine
    rag = RAGEngine(data_dir="./data")
    
    # Check if index exists
    index_path = Path("./index")
    if not index_path.exists():
        print("\nBuilding index (this may take a minute)...")
        rag.build_index()
        rag.save_index("./index")
    else:
        print("\nLoading existing index...")
        rag.load_index("./index")
    
    # Query the system
    query = "Which sensors support high temperatures?"
    print(f"\nQuery: {query}")
    
    results = rag.query(query, top_k=3)
    rag.print_results(results)


def example_2_custom_parameters():
    """Example 2: Using custom parameters."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Custom Parameters")
    print("=" * 80)
    
    # Create RAG with custom chunking
    rag = RAGEngine(
        data_dir="./data",
        chunk_size=800,  # Larger chunks
        overlap=100       # More overlap
    )
    
    print(f"\nChunk size: {rag.chunker.chunk_size}")
    print(f"Overlap: {rag.chunker.overlap}")
    
    # Load index
    try:
        rag.load_index("./index")
        
        # Try different top-k values
        query = "pressure sensors"
        for k in [1, 3, 5]:
            results = rag.query(query, top_k=k)
            print(f"\nTop-{k} results for '{query}':")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['doc_id']} (score: {result['score']:.4f})")
    except FileNotFoundError:
        print("\nError: Index not found. Run example 1 first.")


def example_3_json_export():
    """Example 3: Export results to JSON."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: JSON Export")
    print("=" * 80)
    
    rag = RAGEngine()
    
    try:
        rag.load_index("./index")
        
        query = "flow measurement devices"
        results = rag.query(query, top_k=3)
        
        # Save to JSON
        output_file = "example_results.json"
        rag.save_results_json(results, output_file)
        
        print(f"\nResults saved to {output_file}")
        
        # Show JSON content
        import json
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        print(f"\nJSON contains {len(data)} results")
        print("First result:")
        print(json.dumps(data[0], indent=2))
        
    except FileNotFoundError:
        print("\nError: Index not found. Run example 1 first.")


def example_4_batch_queries():
    """Example 4: Process multiple queries."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Batch Queries")
    print("=" * 80)
    
    rag = RAGEngine()
    
    try:
        rag.load_index("./index")
        
        queries = [
            "temperature measurement",
            "pressure sensors",
            "flow meters",
            "humidity detection",
            "level measurement"
        ]
        
        print(f"\nProcessing {len(queries)} queries...")
        
        for query in queries:
            results = rag.query(query, top_k=1)
            if results:
                result = results[0]
                print(f"\n'{query}' → {result['doc_id']} (score: {result['score']:.4f})")
                
    except FileNotFoundError:
        print("\nError: Index not found. Run example 1 first.")


def example_5_evaluation():
    """Example 5: Evaluate retrieval quality."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Evaluation")
    print("=" * 80)
    
    rag = RAGEngine()
    
    try:
        rag.load_index("./index")
        
        # Run evaluation
        evaluator = RAGEvaluator(rag)
        metrics = evaluator.keyword_recall_at_k(SENSOR_TEST_CASES, top_k=3)
        
        evaluator.print_evaluation_results(metrics)
        
    except FileNotFoundError:
        print("\nError: Index not found. Run example 1 first.")


def example_6_chunk_exploration():
    """Example 6: Explore indexed chunks."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Chunk Exploration")
    print("=" * 80)
    
    rag = RAGEngine()
    
    try:
        rag.load_index("./index")
        
        print(f"\nTotal chunks indexed: {len(rag.chunks)}")
        
        # Group by document
        from collections import defaultdict
        doc_chunks = defaultdict(int)
        
        for chunk in rag.chunks:
            doc_chunks[chunk.doc_id] += 1
        
        print("\nChunks per document:")
        for doc_id, count in sorted(doc_chunks.items()):
            print(f"  {doc_id}: {count} chunks")
        
        # Show a sample chunk
        if rag.chunks:
            sample = rag.chunks[0]
            print(f"\nSample chunk:")
            print(f"  Document: {sample.doc_id}")
            print(f"  Page: {sample.page}")
            print(f"  Text: {sample.text[:200]}...")
            
    except FileNotFoundError:
        print("\nError: Index not found. Run example 1 first.")


def main():
    """Run all examples."""
    print("=" * 80)
    print("Mini-RAG Examples")
    print("=" * 80)
    
    examples = [
        ("Basic Usage", example_1_basic_usage),
        ("Custom Parameters", example_2_custom_parameters),
        ("JSON Export", example_3_json_export),
        ("Batch Queries", example_4_batch_queries),
        ("Evaluation", example_5_evaluation),
        ("Chunk Exploration", example_6_chunk_exploration),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n" + "-" * 80)
    choice = input("\nEnter example number (1-6) or 'all' to run all: ").strip()
    
    if choice.lower() == 'all':
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\nError in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        func()
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()