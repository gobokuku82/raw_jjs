"""
BGE reranker model implementation
"""
import logging
from typing import List, Tuple
import torch
from FlagEmbedding import FlagReranker

from core.simple_config import settings

logger = logging.getLogger(__name__)


class BGEReranker:
    """BGE reranker model wrapper"""
    
    def __init__(self):
        self.model_name = settings.reranker_model
        try:
            self.model = FlagReranker(self.model_name, use_fp16=True)
            logger.info(f"BGE reranker model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading BGE reranker: {e}")
            # Initialize without model for now
            self.model = None
    
    def rerank(self, query: str, documents: List[str], top_k: int = 10) -> List[Tuple[int, float, str]]:
        """Rerank documents based on relevance to query"""
        if not self.model:
            logger.warning("Reranker model not available, returning original order")
            return [(i, 1.0, doc) for i, doc in enumerate(documents[:top_k])]
        
        try:
            # Prepare pairs for reranking
            pairs = [[query, doc] for doc in documents]
            
            # Get reranking scores
            scores = self.model.compute_score(pairs)
            
            # Handle single document case
            if not isinstance(scores, list):
                scores = [scores]
            
            # Create scored results
            scored_docs = [(i, score, doc) for i, (score, doc) in enumerate(zip(scores, documents))]
            
            # Sort by score (descending)
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            return scored_docs[:top_k]
        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            # Fallback to original order
            return [(i, 1.0, doc) for i, doc in enumerate(documents[:top_k])]
    
    def rerank_with_metadata(
        self, 
        query: str, 
        documents: List[dict], 
        content_key: str = "content",
        top_k: int = 10
    ) -> List[dict]:
        """Rerank documents with metadata"""
        if not documents:
            return []
        
        # Extract content for reranking
        contents = [doc.get(content_key, "") for doc in documents]
        
        # Rerank
        reranked = self.rerank(query, contents, top_k)
        
        # Combine with original metadata
        results = []
        for original_idx, score, _ in reranked:
            doc = documents[original_idx].copy()
            doc["rerank_score"] = score
            results.append(doc)
        
        return results
    
    def is_available(self) -> bool:
        """Check if reranker model is available"""
        return self.model is not None
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "available": self.is_available(),
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        } 