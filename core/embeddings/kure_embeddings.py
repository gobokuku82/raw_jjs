"""
KURE-v1 Korean embedding model implementation
"""
import logging
from typing import List
import torch
from sentence_transformers import SentenceTransformer
import numpy as np

from core.simple_config import settings

logger = logging.getLogger(__name__)


class KUREEmbeddings:
    """KURE-v1 Korean embedding model wrapper"""
    
    def __init__(self):
        self.model_name = settings.embedding_model
        self.model = None
        self.dimension = 0
        self._available = False
        
        try:
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self._available = True
            logger.info(f"KURE embeddings model loaded: {self.model_name}, dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Error loading KURE model: {e}")
            try:
                # Fallback to a Korean-compatible model
                self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                self.model = SentenceTransformer(self.model_name)
                self.dimension = self.model.get_sentence_embedding_dimension()
                self._available = True
                logger.warning(f"Fallback to model: {self.model_name}")
            except Exception as e2:
                logger.error(f"Error loading fallback model: {e2}")
                self._available = False
    
    def is_available(self) -> bool:
        """Check if the model is available"""
        return self._available
    
    def encode(self, texts) -> List[List[float]]:
        """Encode texts (alias for embed_texts)"""
        if isinstance(texts, str):
            return [self.embed_text(texts)]
        else:
            return self.embed_texts(texts)
    
    def embed_text(self, text: str) -> List[float]:
        """Embed single text"""
        if not self.is_available():
            logger.warning("KURE model not available, returning zero vector")
            return [0.0] * 768  # Default dimension
            
        try:
            # Preprocess text
            text = self._preprocess_text(text)
            
            # Generate embedding
            embedding = self.model.encode(text, convert_to_tensor=False)
            
            # Ensure it's a list of floats
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            # Return zero vector as fallback
            return [0.0] * (self.dimension or 768)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts"""
        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # Generate embeddings
            embeddings = self.model.encode(processed_texts, convert_to_tensor=False, batch_size=32)
            
            # Ensure it's a list of lists of floats
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding texts: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.dimension] * len(texts)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better embedding quality"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Truncate if too long (most models have max token limits)
        max_chars = 8000  # Conservative limit
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning(f"Text truncated to {max_chars} characters")
        
        return text
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts"""
        try:
            embedding1 = self.embed_text(text1)
            embedding2 = self.embed_text(text2)
            
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def find_similar_chunks(self, query: str, chunks: List[str], top_k: int = 5) -> List[tuple]:
        """Find most similar text chunks to query"""
        try:
            query_embedding = self.embed_text(query)
            chunk_embeddings = self.embed_texts(chunks)
            
            # Compute similarities
            similarities = []
            query_vec = np.array(query_embedding)
            
            for i, chunk_embedding in enumerate(chunk_embeddings):
                chunk_vec = np.array(chunk_embedding)
                similarity = np.dot(query_vec, chunk_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec))
                similarities.append((i, similarity, chunks[i]))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
        except Exception as e:
            logger.error(f"Error finding similar chunks: {e}")
            return []
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "max_seq_length": getattr(self.model, 'max_seq_length', 'unknown')
        } 