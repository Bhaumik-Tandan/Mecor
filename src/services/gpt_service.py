"""GPT service for query enhancement and candidate reranking."""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

from ..config.settings import config
from ..models.candidate import CandidateProfile
from ..utils.logger import get_logger
from ..utils.helpers import retry_with_backoff, load_json_file

logger = get_logger(__name__)


class GPTService:
    """Service for GPT-based query enhancement and candidate reranking."""
    
    def __init__(self):
        if not config.api.openai_api_key:
            logger.warning("OpenAI API key not found. GPT features will be disabled.")
            self.client = None
            return
            
        self.client = OpenAI(api_key=config.api.openai_api_key)
        self.model = "gpt-4.1-nano-2025-04-14"  # Use the available model
        
        # Load prompts configuration
        self.prompts_config = load_json_file("src/config/prompts.json")
        
        logger.info("Initialized GPTService with OpenAI API")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0, backoff_factor=2.0)
    def _make_gpt_request(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.3,
        max_tokens: int = 500
    ) -> str:
        """
        Make a request to the GPT API with retry logic.
        
        Args:
            messages: List of messages for the conversation
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            GPT response text
            
        Raises:
            Exception: If API request fails after retries
        """
        if not self.client:
            raise Exception("GPT service not available - no API key configured")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content.strip()
    
    def enhance_query(self, job_category: str) -> List[str]:
        """
        Generate enhanced search queries for a job category using GPT.
        
        Args:
            job_category: Job category to enhance (e.g., "tax_lawyer")
            
        Returns:
            List of enhanced query strings
        """
        if not self.client:
            logger.warning("GPT service not available for query enhancement")
            return [job_category.replace("_", " ").replace(".yml", "")]
        
        logger.debug(f"Enhancing query for job category: {job_category}")
        
        try:
            prompt_config = self.prompts_config.get("query_enhancement", {})
            system_prompt = prompt_config.get("system_prompt", "You are a helpful assistant.")
            user_prompt_template = prompt_config.get("user_prompt_template", "Enhance this query: {job_category}")
            
            user_prompt = user_prompt_template.format(job_category=job_category)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self._make_gpt_request(
                messages,
                temperature=prompt_config.get("temperature", 0.3),
                max_tokens=prompt_config.get("max_tokens", 500)
            )
            
            # Try to parse JSON response
            try:
                enhanced_queries = json.loads(response)
                if isinstance(enhanced_queries, list):
                    logger.debug(f"Generated {len(enhanced_queries)} enhanced queries")
                    return enhanced_queries
            except json.JSONDecodeError:
                logger.warning("GPT response was not valid JSON, using raw response")
                return [response]
                
        except Exception as e:
            logger.error(f"Failed to enhance query using GPT: {e}")
            # Fallback to simple query
            return [job_category.replace("_", " ").replace(".yml", "")]
    
    def rerank_candidates(
        self, 
        job_category: str, 
        candidates: List[CandidateProfile],
        top_k: int = 10
    ) -> List[CandidateProfile]:
        """
        Rerank candidates using GPT-based evaluation.
        
        Args:
            job_category: Job category for context
            candidates: List of candidates to rerank
            top_k: Number of top candidates to return
            
        Returns:
            Reranked list of candidates
        """
        if not self.client or not candidates:
            logger.warning("GPT service not available or no candidates to rerank")
            return candidates[:top_k]
        
        logger.info(f"Reranking {len(candidates)} candidates using GPT for {job_category}")
        
        try:
            # Prepare candidate information
            candidates_text = ""
            for i, candidate in enumerate(candidates[:20]):  # Limit to top 20 for token efficiency
                summary = (candidate.summary or "")[:200]  # Truncate for token efficiency
                candidates_text += f"{i+1}. ID: {candidate.id} | Name: {candidate.name} | Summary: {summary}\n"
            
            prompt_config = self.prompts_config.get("candidate_reranking", {})
            system_prompt = prompt_config.get("system_prompt", "You are a recruiter.")
            user_prompt_template = prompt_config.get("user_prompt_template", "Rank these candidates: {candidates_text}")
            
            user_prompt = user_prompt_template.format(
                job_category=job_category,
                candidates_text=candidates_text
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self._make_gpt_request(
                messages,
                temperature=prompt_config.get("temperature", 0.1),
                max_tokens=prompt_config.get("max_tokens", 800)
            )
            
            # Try to parse reranked IDs
            try:
                reranked_ids = json.loads(response)
                if isinstance(reranked_ids, list):
                    # Create mapping of ID to candidate
                    id_to_candidate = {c.id: c for c in candidates}
                    
                    # Build reranked list
                    reranked_candidates = []
                    for candidate_id in reranked_ids:
                        if candidate_id in id_to_candidate:
                            reranked_candidates.append(id_to_candidate[candidate_id])
                    
                    # Add any missed candidates at the end
                    reranked_ids_set = set(reranked_ids)
                    for candidate in candidates:
                        if candidate.id not in reranked_ids_set:
                            reranked_candidates.append(candidate)
                    
                    logger.info(f"Successfully reranked candidates using GPT")
                    return reranked_candidates[:top_k]
                    
            except json.JSONDecodeError:
                logger.warning("GPT reranking response was not valid JSON")
                
        except Exception as e:
            logger.error(f"Failed to rerank candidates using GPT: {e}")
        
        # Fallback to original order
        return candidates[:top_k]
    
    def extract_hard_filters(self, job_category: str) -> Dict[str, List[str]]:
        """
        Extract hard filter requirements using GPT.
        
        Args:
            job_category: Job category to analyze
            
        Returns:
            Dictionary with extracted filter criteria
        """
        if not self.client:
            logger.warning("GPT service not available for filter extraction")
            return {"must_have": [], "preferred": [], "exclude": []}
        
        logger.debug(f"Extracting hard filters for: {job_category}")
        
        try:
            prompt_config = self.prompts_config.get("hard_filter_extraction", {})
            system_prompt = prompt_config.get("system_prompt", "You extract requirements.")
            user_prompt_template = prompt_config.get("user_prompt_template", "Extract requirements for: {job_category}")
            
            user_prompt = user_prompt_template.format(job_category=job_category)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self._make_gpt_request(
                messages,
                temperature=prompt_config.get("temperature", 0.2),
                max_tokens=prompt_config.get("max_tokens", 400)
            )
            
            # Try to parse filter requirements
            try:
                filters = json.loads(response)
                if isinstance(filters, dict):
                    logger.debug(f"Extracted hard filters using GPT")
                    return filters
            except json.JSONDecodeError:
                logger.warning("GPT filter extraction response was not valid JSON")
                
        except Exception as e:
            logger.error(f"Failed to extract filters using GPT: {e}")
        
        # Fallback to empty filters
        return {"must_have": [], "preferred": [], "exclude": []}
    
    def is_available(self) -> bool:
        """Check if GPT service is available."""
        return self.client is not None


# Global GPT service instance
gpt_service = GPTService() 