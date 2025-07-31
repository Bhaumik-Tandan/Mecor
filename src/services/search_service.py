"""Search service for candidate retrieval using vector and BM25 search."""
import turbopuffer
import time
import threading
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        self.prompts_config = load_json_file("src/config/prompts.json")
        logger.info(f"Initialized SearchService with namespace: {config.turbopuffer.namespace}")

    def get_domain_queries(self, job_category: str) -> List[str]:
        """Get domain-specific queries for a job category."""
        category_name = job_category.replace("_", " ").replace(".yml", "")
        domain_queries = self.prompts_config.get("domain_specific_queries", {})
        static_queries = domain_queries.get(category_name, [f"professional {category_name}"])
        
        # For failed categories, use GPT enhancement if available
        failed_categories = ['biology_expert', 'anthropology', 'quantitative_finance', 'bankers']
        if any(cat in job_category for cat in failed_categories):
            from ..services.gpt_service import gpt_service
            if gpt_service.is_available():
                try:
                    gpt_queries = gpt_service.generate_enhanced_domain_queries(job_category)
                    if gpt_queries:
                        static_queries = gpt_queries  # Use GPT queries for failed categories
                        logger.info(f"Using GPT-enhanced queries for {job_category}")
                except Exception as e:
                    logger.warning(f"GPT query enhancement failed for {job_category}: {e}")
        
        logger.debug(f"Using {len(static_queries)} queries for {job_category}")
        return static_queries

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
        thread_id = threading.get_ident()
        logger.debug(f"🧵 Thread {thread_id}: Vector search for '{query[:50]}...' (top_k={top_k})")
        
        search_start = time.time()
        
        with PerformanceTimer(f"Vector search for '{query[:50]}...'"):
            embedding = embedding_service.generate_embedding(query)
            results = self.namespace.query(
                rank_by=["vector", "ANN", embedding],
                top_k=top_k,
                include_attributes=["id", "name", "email", "rerank_summary", "linkedin_id", "country"]
            )
            
            candidates = []
            for row in results.rows:
                if hasattr(row, 'id'):
                    candidate = CandidateProfile(
                        id=getattr(row, 'id', ''),
                        name=getattr(row, 'name', ''),
                        email=getattr(row, 'email', ''),
                        summary=getattr(row, 'rerank_summary', ''),
                        linkedin_id=getattr(row, 'linkedin_id', ''),
                        country=getattr(row, 'country', '')
                    )
                    candidates.append(candidate)
            
            search_time = time.time() - search_start
            logger.debug(f"🧵 Thread {thread_id}: Vector search returned {len(candidates)} candidates in {search_time:.2f}s")
            return candidates

    def bm25_search_parallel(
        self, 
        keywords: List[str], 
        top_k: int = 100
    ) -> List[CandidateProfile]:
        """
        Perform BM25 text search with parallel keyword processing.
        
        Args:
            keywords: List of keywords to search for
            top_k: Number of top results to return
        
        Returns:
            List of candidate profiles
        """
        thread_id = threading.get_ident()
        logger.debug(f"🧵 Thread {thread_id}: BM25 search with {len(keywords)} keywords: {keywords[:3]}...")
        
        search_start = time.time()
        
        def search_single_keyword(keyword: str) -> List[CandidateProfile]:
            """Search for a single keyword."""
            inner_thread_id = threading.get_ident()
            try:
                keyword_top_k = max(1, min(top_k // len(keywords), 1200))
                logger.debug(f"🧵 Thread {inner_thread_id}: Searching keyword '{keyword}' (top_k={keyword_top_k})")
                
                keyword_start = time.time()
                results = self.namespace.query(
                    rank_by=["rerank_summary", "BM25", keyword],
                    top_k=keyword_top_k,
                    include_attributes=["id", "name", "email", "rerank_summary", "linkedin_id", "country"]
                )
                
                candidates = []
                for row in results.rows:
                    if hasattr(row, 'id'):
                        candidate = CandidateProfile(
                            id=getattr(row, 'id', ''),
                            name=getattr(row, 'name', ''),
                            email=getattr(row, 'email', ''),
                            summary=getattr(row, 'rerank_summary', ''),
                            linkedin_id=getattr(row, 'linkedin_id', ''),
                            country=getattr(row, 'country', '')
                        )
                        candidates.append(candidate)
                
                keyword_time = time.time() - keyword_start
                logger.debug(f"🧵 Thread {inner_thread_id}: Keyword '{keyword}' returned {len(candidates)} candidates in {keyword_time:.2f}s")
                return candidates
                
            except Exception as e:
                logger.warning(f"🧵 Thread {inner_thread_id}: BM25 search failed for keyword '{keyword}': {e}")
                return []
        
        # Use parallel execution for keyword searches
        max_keyword_workers = min(len(keywords), config.search.thread_pool_size)
        logger.debug(f"🧵 Thread {thread_id}: Using {max_keyword_workers} workers for {len(keywords)} keywords")
        
        all_candidates = []
        with ThreadPoolExecutor(max_workers=max_keyword_workers) as executor:
            future_to_keyword = {
                executor.submit(search_single_keyword, keyword): keyword
                for keyword in keywords
            }
            
            for future in as_completed(future_to_keyword):
                keyword = future_to_keyword[future]
                try:
                    candidates = future.result()
                    all_candidates.extend(candidates)
                    logger.debug(f"🧵 Thread {thread_id}: Completed keyword '{keyword}' - {len(candidates)} candidates")
                except Exception as e:
                    logger.warning(f"🧵 Thread {thread_id}: Failed to get results for keyword '{keyword}': {e}")
        
        # Deduplicate candidates
        seen = set()
        unique_candidates = []
        for candidate in all_candidates:
            if candidate.id not in seen:
                seen.add(candidate.id)
                unique_candidates.append(candidate)
        
        search_time = time.time() - search_start
        logger.debug(f"🧵 Thread {thread_id}: BM25 parallel search completed: {len(unique_candidates)} unique candidates in {search_time:.2f}s")
        return unique_candidates[:top_k]

    def bm25_search(
        self, 
        keywords: List[str], 
        top_k: int = 100
    ) -> List[CandidateProfile]:
        """
        Perform BM25 text search - delegates to parallel implementation.
        
        Args:
            keywords: List of keywords to search for
            top_k: Number of top results to return
        
        Returns:
            List of candidate profiles
        """
        return self.bm25_search_parallel(keywords, top_k)

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

        thread_id = threading.get_ident()
        filter_start = time.time()
        
        must_have = hard_filters.get("must_have", [])
        exclude = hard_filters.get("exclude", [])
        
        filtered_candidates = []
        for candidate in candidates:
            if candidate.satisfies_hard_filters(must_have, exclude):
                filtered_candidates.append(candidate)
        
        filter_time = time.time() - filter_start
        logger.info(f"🧵 Thread {thread_id}: Hard filters reduced candidates from {len(candidates)} to {len(filtered_candidates)} in {filter_time:.2f}s")
        return filtered_candidates

    def hybrid_search_enhanced(
        self, 
        query: SearchQuery, 
        search_config: SearchConfig
    ) -> List[CandidateProfile]:
        """
        Perform enhanced hybrid search with better parallelization.
        
        Args:
            query: Search query object
            search_config: Search configuration
        
        Returns:
            List of ranked candidates
        """
        thread_id = threading.get_ident()
        logger.info(f"🧵 Thread {thread_id}: Starting enhanced hybrid search for: {query.job_category}")
        
        search_start = time.time()
        candidate_scores: Dict[str, CandidateScores] = {}
        
        with PerformanceTimer(f"Enhanced hybrid search for {query.job_category}"):
            # Phase 1: Parallel vector searches
            logger.debug(f"🧵 Thread {thread_id}: Phase 1 - Vector searches")
            vector_start = time.time()
            
            domain_queries = self.get_domain_queries(query.job_category)
            all_vector_queries = [query.query_text] + domain_queries
            vector_top_k = min(100, max(10, query.max_candidates))
            
            vector_tasks = [
                lambda q=q: self.vector_search(q, vector_top_k)
                for q in all_vector_queries
            ]
            
            vector_results = execute_parallel_tasks(
                vector_tasks, 
                max_workers=min(len(all_vector_queries), config.search.thread_pool_size)
            )
            
            # Process vector results
            for i, candidates in enumerate(vector_results):
                if candidates:
                    weight = 1.0 / (i + 1)  # Decreasing weight for additional queries
                    for j, candidate in enumerate(candidates):
                        score = (1.0 / (j + 1)) * weight  # Position-based scoring
                        if candidate.id not in candidate_scores:
                            candidate_scores[candidate.id] = CandidateScores(candidate.id)
                        candidate_scores[candidate.id].vector_score += score
            
            vector_time = time.time() - vector_start
            logger.debug(f"🧵 Thread {thread_id}: Vector searches completed in {vector_time:.2f}s")
            
            # Phase 2: Parallel BM25 search
            logger.debug(f"🧵 Thread {thread_id}: Phase 2 - BM25 search")
            bm25_start = time.time()
            
            keywords = self.get_bm25_keywords(query.job_category)
            bm25_top_k = min(100, max(10, query.max_candidates))
            bm25_candidates = self.bm25_search_parallel(keywords, bm25_top_k)
            
            # Process BM25 results
            for j, candidate in enumerate(bm25_candidates):
                score = 1.0 / (j + 1)  # Position-based scoring
                if candidate.id not in candidate_scores:
                    candidate_scores[candidate.id] = CandidateScores(candidate.id)
                candidate_scores[candidate.id].bm25_score += score
            
            bm25_time = time.time() - bm25_start
            logger.debug(f"🧵 Thread {thread_id}: BM25 search completed in {bm25_time:.2f}s")
            
            # Phase 3: Soft filtering
            logger.debug(f"🧵 Thread {thread_id}: Phase 3 - Soft filtering")
            soft_filter_start = time.time()
            
            hard_filters = self.get_hard_filters(query.job_category)
            preferred_keywords = hard_filters.get("preferred", [])
            
            if preferred_keywords:
                all_candidate_ids = list(candidate_scores.keys())
                candidates_for_soft_filtering = self._get_candidate_profiles_batch(all_candidate_ids)
                
                for candidate in candidates_for_soft_filtering:
                    if candidate.id in candidate_scores:
                        soft_score = candidate.calculate_soft_filter_score(preferred_keywords)
                        candidate_scores[candidate.id].soft_filter_score = soft_score
                
                soft_filter_time = time.time() - soft_filter_start
                logger.debug(f"🧵 Thread {thread_id}: Soft filters applied with {len(preferred_keywords)} keywords in {soft_filter_time:.2f}s")
            
            # Phase 4: Score calculation and ranking
            logger.debug(f"🧵 Thread {thread_id}: Phase 4 - Scoring and ranking")
            scoring_start = time.time()
            
            for candidate_score in candidate_scores.values():
                candidate_score.calculate_combined_score(
                    config.search.vector_search_weight,
                    config.search.bm25_search_weight,
                    config.search.soft_filter_weight
                )
            
            sorted_scores = sorted(
                candidate_scores.values(),
                key=lambda x: x.combined_score,
                reverse=True
            )
            
            top_candidate_ids = [cs.candidate_id for cs in sorted_scores[:query.max_candidates]]
            final_candidates = self._get_candidate_profiles_batch(top_candidate_ids)
            
            scoring_time = time.time() - scoring_start
            logger.debug(f"🧵 Thread {thread_id}: Scoring completed in {scoring_time:.2f}s")
            
            # Phase 5: Hard filtering
            if search_config.use_hard_filters:
                logger.debug(f"🧵 Thread {thread_id}: Phase 5 - Hard filtering")
                hard_filters = self.get_hard_filters(query.job_category)
                final_candidates = self.apply_hard_filters(final_candidates, hard_filters)
            
            total_search_time = time.time() - search_start
            logger.info(f"🧵 Thread {thread_id}: Enhanced hybrid search completed: {len(final_candidates)} candidates in {total_search_time:.2f}s")
            
            return final_candidates[:query.max_candidates]

    def hybrid_search(
        self, 
        query: SearchQuery, 
        search_config: SearchConfig
    ) -> List[CandidateProfile]:
        """
        Perform hybrid search - delegates to enhanced implementation.
        """
        return self.hybrid_search_enhanced(query, search_config)

    def enhanced_domain_search(
        self, 
        query: SearchQuery, 
        search_config: SearchConfig
    ) -> List[CandidateProfile]:
        """
        Simple domain-specific search using hybrid approach.
        
        Args:
            query: Search query object
            search_config: Search configuration
        
        Returns:
            List of ranked candidates
        """
        logger.info(f"Starting search for: {query.job_category}")
        
        # Use simple hybrid search for all categories
        candidates = self.hybrid_search_enhanced(query, search_config)
        
        logger.info(f"Found {len(candidates)} candidates for {query.job_category}")
        return candidates

    def _get_candidate_profiles_batch(self, candidate_ids: List[str]) -> List[CandidateProfile]:
        """
        Retrieve full candidate profiles for given IDs with batch processing.
        
        Args:
            candidate_ids: List of candidate IDs
        
        Returns:
            List of candidate profiles
        """
        if not candidate_ids:
            return []
        
        thread_id = threading.get_ident()
        batch_start = time.time()
        
        logger.debug(f"🧵 Thread {thread_id}: Retrieving {len(candidate_ids)} candidate profiles")
        
        def get_single_profile(candidate_id: str) -> Optional[CandidateProfile]:
            """Get a single candidate profile."""
            try:
                dummy_vector = [0.0] * 1024
                results = self.namespace.query(
                    rank_by=["vector", "ANN", dummy_vector],
                    top_k=1,
                    filters=["id", "Eq", candidate_id],
                    include_attributes=["id", "name", "email", "rerank_summary", "linkedin_id", "country"]
                )
                
                if results.rows:
                    row = results.rows[0]
                    candidate = CandidateProfile(
                        id=getattr(row, 'id', ''),
                        name=getattr(row, 'name', ''),
                        email=getattr(row, 'email', ''),
                        summary=getattr(row, 'rerank_summary', ''),
                        linkedin_id=getattr(row, 'linkedin_id', ''),
                        country=getattr(row, 'country', '')
                    )
                    return candidate
                return None
            except Exception as e:
                logger.warning(f"🧵 Thread {threading.get_ident()}: Failed to retrieve candidate {candidate_id}: {e}")
                return None
        
        # Use parallel processing for batch retrieval
        max_profile_workers = min(len(candidate_ids), config.search.thread_pool_size)
        candidates = []
        
        with ThreadPoolExecutor(max_workers=max_profile_workers) as executor:
            future_to_id = {
                executor.submit(get_single_profile, candidate_id): candidate_id
                for candidate_id in candidate_ids
            }
            
            for future in as_completed(future_to_id):
                candidate_id = future_to_id[future]
                try:
                    candidate = future.result()
                    if candidate:
                        candidates.append(candidate)
                except Exception as e:
                    logger.warning(f"🧵 Thread {thread_id}: Failed to get profile for {candidate_id}: {e}")
        
        batch_time = time.time() - batch_start
        logger.debug(f"🧵 Thread {thread_id}: Retrieved {len(candidates)} profiles in {batch_time:.2f}s")
        
        return candidates

    def _get_candidate_profiles(self, candidate_ids: List[str]) -> List[CandidateProfile]:
        """
        Retrieve full candidate profiles - delegates to batch implementation.
        """
        return self._get_candidate_profiles_batch(candidate_ids)

    def search_candidates(
        self, 
        query: SearchQuery, 
        strategy: SearchStrategy = SearchStrategy.HYBRID
    ) -> List[CandidateProfile]:
        """
        Search for candidates using the specified strategy.
        
        Args:
            query: Search query object
            strategy: Search strategy to use
            
        Returns:
            List of candidate profiles
        """
        search_config = SearchConfig(
            strategy=strategy,
            max_candidates=query.max_candidates,
            vector_weight=config.search.vector_search_weight,
            bm25_weight=config.search.bm25_search_weight,
            use_hard_filters=True
        )
        
        if strategy == SearchStrategy.VECTOR_ONLY:
            return self.vector_search(query.query_text, query.max_candidates)
        elif strategy == SearchStrategy.BM25_ONLY:
            return self.bm25_search(query.job_category, query.max_candidates)
        elif strategy == SearchStrategy.HYBRID:
            # Use enhanced domain search for better precision
            return self.enhanced_domain_search(query, search_config)
        elif strategy == SearchStrategy.GPT_ENHANCED:
            # For GPT enhanced, use both enhanced search and GPT reranking
            candidates = self.enhanced_domain_search(query, search_config)
            from ..services.gpt_service import gpt_service
            if gpt_service.is_available() and candidates:
                try:
                    candidates = gpt_service.rerank_candidates(
                        query.job_category, candidates, query.max_candidates
                    )
                except Exception as e:
                    logger.warning(f"GPT reranking failed: {e}")
            return candidates
        else:
            # Default to enhanced hybrid search
            return self.enhanced_domain_search(query, search_config)
search_service = SearchService() 