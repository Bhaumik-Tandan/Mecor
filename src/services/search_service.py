"""Search service for candidate retrieval using vector and BM25 search."""

import turbopuffer
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from ..config.settings import config
from ..models.candidate import (
    CandidateProfile, SearchResult, SearchQuery, CandidateScores, SearchStrategy
)
from ..services.embedding_service import embedding_service
from ..utils.logger import get_logger
from ..utils.helpers import (
    load_json_file, execute_parallel_tasks, calculate_weighted_score, PerformanceTimer
)

logger = get_logger(__name__)


@dataclass
class SearchConfig:
    """Configuration for individual search operations."""
    strategy: SearchStrategy
    max_candidates: int
    vector_weight: float = 0.6
    bm25_weight: float = 0.4
    use_hard_filters: bool = True


class SearchService:
    """Service for searching candidates using multiple strategies."""
    
    def __init__(self):
        self.tpuf = turbopuffer.Turbopuffer(
            api_key=config.api.turbopuffer_api_key,
            region=config.turbopuffer.region
        )
        self.namespace = self.tpuf.namespace(config.turbopuffer.namespace)
        
        # Load search configurations from JSON
        self.prompts_config = load_json_file("src/config/prompts.json")
        
        logger.info(f"Initialized SearchService with namespace: {config.turbopuffer.namespace}")
    
    def get_domain_queries(self, job_category: str) -> List[str]:
        """
        Get domain-specific queries for a job category.
        
        Args:
            job_category: Job category name (e.g., "tax_lawyer")
            
        Returns:
            List of domain-specific query strings
        """
        category_name = job_category.replace("_", " ").replace(".yml", "")
        domain_queries = self.prompts_config.get("domain_specific_queries", {})
        
        return domain_queries.get(category_name, [f"professional {category_name}"])
    
    def get_bm25_keywords(self, job_category: str) -> List[str]:
        """
        Get BM25 keywords for a job category.
        
        Args:
            job_category: Job category name
            
        Returns:
            List of BM25 search keywords
        """
        category_name = job_category.replace("_", " ").replace(".yml", "")
        bm25_keywords = self.prompts_config.get("bm25_keywords", {})
        
        return bm25_keywords.get(category_name, category_name.split())
    
    def get_hard_filters(self, job_category: str) -> Dict[str, List[str]]:
        """
        Get hard filter criteria for a job category.
        
        Args:
            job_category: Job category name
            
        Returns:
            Dictionary with must_have, preferred, and exclude criteria
        """
        category_name = job_category.replace("_", " ").replace(".yml", "")
        hard_filters = self.prompts_config.get("hard_filters", {})
        
        return hard_filters.get(category_name, {
            "must_have": [],
            "preferred": [],
            "exclude": []
        })
    
    def vector_search(
        self, 
        query: str, 
        top_k: int = 100
    ) -> List[CandidateProfile]:
        """
        Perform vector similarity search.
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            
        Returns:
            List of candidate profiles
        """
        logger.debug(f"Performing vector search: {query[:100]}...")
        
        with PerformanceTimer(f"Vector search for '{query[:50]}...'"):
            # Generate embedding
            embedding = embedding_service.generate_embedding(query)
            
            # Perform vector search
            results = self.namespace.query(
                rank_by=["vector", "ANN", embedding],
                top_k=top_k,
                include_attributes=["id", "name", "email", "rerank_summary"]
            )
            
            candidates = []
            for row in results.rows:
                if hasattr(row, 'id'):
                    candidate = CandidateProfile(
                        id=getattr(row, 'id', ''),
                        name=getattr(row, 'name', ''),
                        email=getattr(row, 'email', ''),
                        summary=getattr(row, 'rerank_summary', '')
                    )
                    candidates.append(candidate)
            
            logger.debug(f"Vector search returned {len(candidates)} candidates")
            return candidates
    
    def bm25_search(
        self, 
        keywords: List[str], 
        top_k: int = 100
    ) -> List[CandidateProfile]:
        """
        Perform BM25 text search.
        
        Args:
            keywords: List of keywords to search for
            top_k: Number of top results to return
            
        Returns:
            List of candidate profiles
        """
        logger.debug(f"Performing BM25 search with keywords: {keywords}")
        
        all_candidates = []
        
        for keyword in keywords:
            try:
                results = self.namespace.query(
                    rank_by=["rerank_summary", "BM25", keyword],
                    top_k=top_k // len(keywords),
                    include_attributes=["id", "name", "email", "rerank_summary"]
                )
                
                for row in results.rows:
                    if hasattr(row, 'id'):
                        candidate = CandidateProfile(
                            id=getattr(row, 'id', ''),
                            name=getattr(row, 'name', ''),
                            email=getattr(row, 'email', ''),
                            summary=getattr(row, 'rerank_summary', '')
                        )
                        all_candidates.append(candidate)
                        
            except Exception as e:
                logger.warning(f"BM25 search failed for keyword '{keyword}': {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in all_candidates:
            if candidate.id not in seen:
                seen.add(candidate.id)
                unique_candidates.append(candidate)
        
        logger.debug(f"BM25 search returned {len(unique_candidates)} unique candidates")
        return unique_candidates[:top_k]
    
    def apply_hard_filters(
        self, 
        candidates: List[CandidateProfile], 
        hard_filters: Dict[str, List[str]]
    ) -> List[CandidateProfile]:
        """
        Apply hard filters to candidate list.
        
        Args:
            candidates: List of candidates to filter
            hard_filters: Dictionary with filtering criteria
            
        Returns:
            Filtered list of candidates
        """
        if not hard_filters:
            return candidates
        
        must_have = hard_filters.get("must_have", [])
        exclude = hard_filters.get("exclude", [])
        
        filtered_candidates = []
        
        for candidate in candidates:
            if candidate.satisfies_hard_filters(must_have, exclude):
                filtered_candidates.append(candidate)
        
        logger.info(f"Hard filters reduced candidates from {len(candidates)} to {len(filtered_candidates)}")
        return filtered_candidates
    
    def hybrid_search(
        self, 
        query: SearchQuery, 
        search_config: SearchConfig
    ) -> List[CandidateProfile]:
        """
        Perform hybrid search combining vector and BM25 results.
        
        Args:
            query: Search query object
            search_config: Search configuration
            
        Returns:
            List of ranked candidates
        """
        logger.info(f"Starting hybrid search for: {query.job_category}")
        
        candidate_scores: Dict[str, CandidateScores] = {}
        
        with PerformanceTimer(f"Hybrid search for {query.job_category}"):
            
            # 1. Vector Search with multiple query variations
            domain_queries = self.get_domain_queries(query.job_category)
            all_vector_queries = [query.query_text] + domain_queries
            
            vector_tasks = [
                lambda q=q: self.vector_search(q, search_config.max_candidates // 2)
                for q in all_vector_queries
            ]
            
            vector_results = execute_parallel_tasks(
                vector_tasks, 
                max_workers=config.search.thread_pool_size
            )
            
            # Aggregate vector scores
            for i, candidates in enumerate(vector_results):
                if candidates:
                    weight = 1.0 / (i + 1)  # Decreasing weight for additional queries
                    for j, candidate in enumerate(candidates):
                        score = (1.0 / (j + 1)) * weight  # Position-based scoring
                        
                        if candidate.id not in candidate_scores:
                            candidate_scores[candidate.id] = CandidateScores(candidate.id)
                        
                        candidate_scores[candidate.id].vector_score += score
            
            # 2. BM25 Search
            keywords = self.get_bm25_keywords(query.job_category)
            bm25_candidates = self.bm25_search(keywords, search_config.max_candidates)
            
            for j, candidate in enumerate(bm25_candidates):
                score = 1.0 / (j + 1)  # Position-based scoring
                
                if candidate.id not in candidate_scores:
                    candidate_scores[candidate.id] = CandidateScores(candidate.id)
                
                candidate_scores[candidate.id].bm25_score += score
            
            # 3. Calculate combined scores
            for candidate_score in candidate_scores.values():
                candidate_score.calculate_combined_score(
                    search_config.vector_weight,
                    search_config.bm25_weight
                )
            
            # 4. Get top candidates
            sorted_scores = sorted(
                candidate_scores.values(),
                key=lambda x: x.combined_score,
                reverse=True
            )
            
            # 5. Retrieve full candidate profiles
            top_candidate_ids = [cs.candidate_id for cs in sorted_scores[:search_config.max_candidates]]
            final_candidates = self._get_candidate_profiles(top_candidate_ids)
            
            # 6. Apply hard filters if enabled
            if search_config.use_hard_filters:
                hard_filters = self.get_hard_filters(query.job_category)
                final_candidates = self.apply_hard_filters(final_candidates, hard_filters)
            
            logger.info(f"Hybrid search completed: {len(final_candidates)} candidates")
            return final_candidates[:query.max_candidates]
    
    def _get_candidate_profiles(self, candidate_ids: List[str]) -> List[CandidateProfile]:
        """
        Retrieve full candidate profiles for given IDs.
        
        Args:
            candidate_ids: List of candidate IDs
            
        Returns:
            List of candidate profiles
        """
        candidates = []
        
        for candidate_id in candidate_ids:
            try:
                # Use a dummy vector for ID-based lookup
                dummy_vector = [0.0] * 1024
                results = self.namespace.query(
                    rank_by=["vector", "ANN", dummy_vector],
                    top_k=1,
                    filters=["id", "Eq", candidate_id],
                    include_attributes=["id", "name", "email", "rerank_summary"]
                )
                
                if results.rows:
                    row = results.rows[0]
                    candidate = CandidateProfile(
                        id=getattr(row, 'id', ''),
                        name=getattr(row, 'name', ''),
                        email=getattr(row, 'email', ''),
                        summary=getattr(row, 'rerank_summary', '')
                    )
                    candidates.append(candidate)
                    
            except Exception as e:
                logger.warning(f"Failed to retrieve candidate {candidate_id}: {e}")
        
        return candidates
    
    def search_candidates(
        self, 
        query: SearchQuery, 
        strategy: SearchStrategy = SearchStrategy.HYBRID
    ) -> List[CandidateProfile]:
        """
        Main entry point for candidate search.
        
        Args:
            query: Search query object
            strategy: Search strategy to use
            
        Returns:
            List of ranked candidates
        """
        search_config = SearchConfig(
            strategy=strategy,
            max_candidates=query.max_candidates,
            vector_weight=config.search.vector_search_weight,
            bm25_weight=config.search.bm25_search_weight
        )
        
        if strategy == SearchStrategy.VECTOR_ONLY:
            return self.vector_search(query.query_text, query.max_candidates)
        elif strategy == SearchStrategy.BM25_ONLY:
            keywords = self.get_bm25_keywords(query.job_category)
            return self.bm25_search(keywords, query.max_candidates)
        elif strategy == SearchStrategy.HYBRID:
            return self.hybrid_search(query, search_config)
        else:
            logger.warning(f"Unsupported search strategy: {strategy}")
            return self.hybrid_search(query, search_config)


# Global search service instance
search_service = SearchService() 