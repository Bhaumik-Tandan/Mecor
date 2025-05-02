"""Embedding service for generating vector embeddings using Voyage API."""

import requests
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config.settings import config
from ..utils.logger import get_logger
from ..utils.helpers import retry_with_backoff, execute_parallel_tasks

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating vector embeddings using Voyage AI."""
    
    def __init__(self):
        self.api_key = config.api.voyage_api_key
        self.base_url = "https://api.voyageai.com/v1/embeddings"
        self.model = "voyage-3"
        
        if not self.api_key:
            raise ValueError("VOYAGE_API_KEY not found in environment variables")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0, backoff_factor=2.0)
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Input text to embed
            
        Returns:
            Vector embedding as list of floats
            
        Raises:
            requests.RequestException: If API request fails
            ValueError: If response format is invalid
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": text
        }
        
        logger.debug(f"Generating embedding for text: {text[:100]}...")
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=config.search.request_timeout
        )
        
        response.raise_for_status()
        
        try:
            data = response.json()
            embedding = data["data"][0]["embedding"]
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response format from Voyage API: {e}")
            raise ValueError(f"Invalid embedding response format: {e}")
    
    def generate_embeddings_batch(
        self, 
        texts: List[str], 
        max_workers: int = None
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in parallel.
        
        Args:
            texts: List of texts to embed
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of embeddings corresponding to input texts
        """
        if not texts:
            return []
        
        if max_workers is None:
            max_workers = min(config.search.thread_pool_size, len(texts))
        
        logger.info(f"Generating embeddings for {len(texts)} texts using {max_workers} workers")
        
        # Create tasks for parallel execution
        tasks = [lambda text=text: self.generate_embedding(text) for text in texts]
        
        # Execute tasks in parallel
        embeddings = execute_parallel_tasks(tasks, max_workers=max_workers)
        
        # Filter out None results (failed embeddings)
        successful_embeddings = [emb for emb in embeddings if emb is not None]
        
        logger.info(f"Successfully generated {len(successful_embeddings)}/{len(texts)} embeddings")
        
        return successful_embeddings
    
    def generate_query_variations_embeddings(
        self, 
        base_query: str, 
        variations: List[str]
    ) -> Dict[str, List[float]]:
        """
        Generate embeddings for a base query and its variations.
        
        Args:
            base_query: Original query text
            variations: List of query variations
            
        Returns:
            Dictionary mapping query text to embedding
        """
        all_queries = [base_query] + variations
        embeddings = self.generate_embeddings_batch(all_queries)
        
        result = {}
        for i, query in enumerate(all_queries):
            if i < len(embeddings) and embeddings[i] is not None:
                result[query] = embeddings[i]
        
        return result


# Global embedding service instance
embedding_service = EmbeddingService() 