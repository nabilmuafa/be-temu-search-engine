from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
import torch

class RerankerService:
    def __init__(self):
        """Initialize the reranker service with a cross-encoder model."""
        print("Loading reranker model...")
        # Use a lightweight cross-encoder model specifically trained for reranking
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')
        print("Reranker model loaded successfully")

    def rerank(self, query: str, results: List[Dict[Any, Any]], top_k: int = 10) -> List[Dict[Any, Any]]:
        """
        Rerank search results using the cross-encoder model.
        
        Args:
            query: Original search query
            results: List of search results from Elasticsearch
            top_k: Number of results to return after reranking
            
        Returns:
            Reranked list of results
        """
        if not results:
            return results

        # Prepare pairs of (query, document text) for scoring
        pairs = [(query, f"{result['title']} {result['plot'][:300]}") for result in results]
        
        # Get similarity scores from the cross-encoder
        scores = self.model.predict(pairs)
        
        # Combine results with their scores
        scored_results = list(zip(results, scores))
        
        # Sort by score in descending order and get top_k
        reranked_results = sorted(scored_results, key=lambda x: x[1], reverse=True)[:top_k]
        
        # Add scores to results and return just the documents
        final_results = []
        for doc, score in reranked_results:
            doc['rerank_score'] = float(score)  # Convert to float for JSON serialization
            final_results.append(doc)
            
        return final_results 