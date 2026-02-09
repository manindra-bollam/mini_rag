"""
Evaluation module for testing retrieval quality.

Implements simple recall proxy using keyword matching.
"""
from typing import List, Dict, Tuple
from src.rag_engine import RAGEngine


class RAGEvaluator:
    """Evaluates RAG system performance using simple metrics."""
    
    def __init__(self, rag_engine: RAGEngine):
        """
        Initialize evaluator.
        
        Args:
            rag_engine: RAG engine to evaluate
        """
        self.rag = rag_engine
        
    def keyword_recall_at_k(
        self, 
        test_cases: List[Dict[str, any]], 
        top_k: int = 3
    ) -> Dict[str, float]:
        """
        Evaluate recall using keyword matching.
        
        A test case is considered successful if any of the expected keywords
        appear in the top-k retrieved chunks.
        
        Args:
            test_cases: List of dicts with 'query' and 'expected_keywords'
            top_k: Number of results to retrieve
            
        Returns:
            Dict with evaluation metrics
        """
        total = len(test_cases)
        hits = 0
        results = []
        
        for test_case in test_cases:
            query = test_case['query']
            expected_keywords = test_case['expected_keywords']
            
            # Get results
            retrieved = self.rag.query(query, top_k=top_k)
            
            # Check if any keyword appears in retrieved chunks
            hit = False
            for result in retrieved:
                text_lower = result['text'].lower()
                if any(keyword.lower() in text_lower for keyword in expected_keywords):
                    hit = True
                    break
            
            if hit:
                hits += 1
                
            results.append({
                'query': query,
                'hit': hit,
                'top_result_score': retrieved[0]['score'] if retrieved else 0.0
            })
        
        recall = hits / total if total > 0 else 0.0
        
        return {
            'recall_at_k': recall,
            'total_queries': total,
            'successful_hits': hits,
            'failed_queries': total - hits,
            'detailed_results': results
        }
    
    def print_evaluation_results(self, metrics: Dict[str, any]) -> None:
        """
        Print evaluation results in a formatted way.
        
        Args:
            metrics: Evaluation metrics dictionary
        """
        print("\n" + "=" * 80)
        print("EVALUATION RESULTS")
        print("=" * 80)
        
        print(f"\nRecall@K: {metrics['recall_at_k']:.2%}")
        print(f"Total Queries: {metrics['total_queries']}")
        print(f"Successful Hits: {metrics['successful_hits']}")
        print(f"Failed Queries: {metrics['failed_queries']}")
        
        if metrics['detailed_results']:
            print("\nDetailed Results:")
            print("-" * 80)
            for i, result in enumerate(metrics['detailed_results'], 1):
                status = "✓" if result['hit'] else "✗"
                print(f"{status} Query {i}: {result['query']}")
                print(f"  Top Score: {result['top_result_score']:.4f}")


# Example test cases for sensor PDFs
SENSOR_TEST_CASES = [
    {
        'query': 'Which sensors support 1200°C?',
        'expected_keywords': ['Type K', 'Type N', '1200', '1300', 'thermocouple']
    },
    {
        'query': 'What is the accuracy of RTD sensors?',
        'expected_keywords': ['RTD', 'PT100', '0.15', '0.35', 'accuracy']
    },
    {
        'query': 'pressure measurement strain gauge',
        'expected_keywords': ['strain gauge', 'pressure', '10,000 psi']
    },
    {
        'query': 'non-invasive flow measurement',
        'expected_keywords': ['ultrasonic', 'non-invasive', 'no pressure drop']
    },
    {
        'query': 'humidity sensors temperature range',
        'expected_keywords': ['humidity', 'capacitive', '-40', '125', 'temperature']
    },
    {
        'query': 'radar level sensors',
        'expected_keywords': ['radar', 'level', 'immune', 'foam', 'vapor']
    },
]


if __name__ == "__main__":
    import sys
    
    # Load RAG engine
    print("Loading RAG engine...")
    rag = RAGEngine()
    
    try:
        rag.load_index("./index")
    except FileNotFoundError:
        print("Error: Index not found. Please build the index first.")
        print("Run: python rag.py --build")
        sys.exit(1)
    
    # Run evaluation
    evaluator = RAGEvaluator(rag)
    
    print("\nRunning evaluation with keyword recall test...")
    metrics = evaluator.keyword_recall_at_k(SENSOR_TEST_CASES, top_k=3)
    
    evaluator.print_evaluation_results(metrics)