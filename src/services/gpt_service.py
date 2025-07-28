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

    def validate_candidate_domain_fit(
        self, 
        candidate: CandidateProfile, 
        job_category: str
    ) -> Dict[str, float]:
        """
        Use GPT to validate if a candidate truly fits a specific domain.
        
        Args:
            candidate: Candidate profile to evaluate
            job_category: Target job category
            
        Returns:
            Dictionary with relevance_score (0-1), confidence (0-1), and reasoning
        """
        domain_name = job_category.replace("_", " ").replace(".yml", "")
        
        # Create comprehensive candidate summary
        candidate_text = f"""
        Name: {candidate.name}
        Summary: {candidate.summary or 'No summary available'}
        """
        
        prompt = f"""
        Evaluate how well this candidate fits the role: {domain_name}
        
        Candidate Profile:
        {candidate_text}
        
        Please analyze:
        1. Domain expertise alignment - Does their background truly match this field?
        2. Educational background relevance - Is their education specifically relevant?
        3. Professional experience fit - Does their work experience align?
        4. Specialization match - Are their specializations relevant to this domain?
        
        Scoring Guidelines:
        - 0.9-1.0: Perfect match, clearly belongs in this domain
        - 0.7-0.8: Good match, relevant but may have some gaps
        - 0.5-0.6: Moderate match, partially relevant
        - 0.3-0.4: Poor match, limited relevance
        - 0.0-0.2: No match, clearly wrong domain
        
        Examples:
        - Biology PhD for "mathematics phd" = 0.1 (wrong domain entirely)
        - Math PhD for "mathematics phd" = 0.95 (perfect match)
        - Applied Math PhD for "quantitative finance" = 0.85 (relevant cross-over)
        
        Return JSON:
        {{
            "relevance_score": 0.85,
            "confidence": 0.9,
            "reasoning": "Brief explanation of why this score was given",
            "red_flags": ["Any obvious mismatches or concerns"],
            "domain_keywords_found": ["Relevant keywords from their profile"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert recruiter with deep knowledge across all professional domains. You excel at identifying genuine domain expertise vs superficial keyword matches."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=600
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            result = json.loads(result_text)
            
            # Validate and sanitize the response
            return {
                "relevance_score": max(0.0, min(1.0, result.get("relevance_score", 0.0))),
                "confidence": max(0.0, min(1.0, result.get("confidence", 0.0))),
                "reasoning": result.get("reasoning", "No reasoning provided"),
                "red_flags": result.get("red_flags", []),
                "domain_keywords_found": result.get("domain_keywords_found", [])
            }
            
        except Exception as e:
            logger.error(f"Domain validation failed: {e}")
            return {
                "relevance_score": 0.5,  # Neutral score on failure
                "confidence": 0.0,
                "reasoning": f"GPT validation failed: {e}",
                "red_flags": ["GPT validation error"],
                "domain_keywords_found": []
            }
    
    def generate_enhanced_domain_queries(self, job_category: str) -> List[str]:
        """
        Generate highly specific, domain-focused search queries using GPT.
        
        Args:
            job_category: Job category to generate queries for
            
        Returns:
            List of enhanced search queries
        """
        domain_name = job_category.replace("_", " ").replace(".yml", "")
        
        prompt = f"""
        Generate 5 highly specific search queries for finding ONLY candidates who are true experts in: {domain_name}
        
        Requirements:
        1. Be extremely specific to avoid cross-domain contamination
        2. Include domain-specific terminology and qualifications
        3. Focus on distinguishing this field from similar fields
        4. Include specific experience indicators and credentials
        5. Avoid generic terms that could match other domains
        
        Examples:
        For "mathematics phd":
        - Include: pure mathematics, applied mathematics, mathematical analysis, number theory, topology
        - Avoid: general "research", "professor" (too broad)
        
        For "biology expert":
        - Include: molecular biology, cell biology, genomics, biotechnology, life sciences
        - Avoid: general "scientist", "research" (too broad)
        
        For "radiology":
        - Include: diagnostic imaging, medical imaging, radiologic technology, DICOM
        - Avoid: general "medical", "doctor" (too broad)
        
        Return ONLY a JSON array of 5 specific queries:
        ["query1", "query2", "query3", "query4", "query5"]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert recruiter who specializes in creating precise, domain-specific search queries that avoid false matches across different fields."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=400
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            queries = json.loads(result_text)
            
            if isinstance(queries, list) and len(queries) > 0:
                return queries[:5]  # Ensure max 5 queries
            else:
                logger.warning(f"Invalid query format from GPT for {job_category}")
                return [f"expert {domain_name} professional specialist"]
                
        except Exception as e:
            logger.error(f"Enhanced query generation failed: {e}")
            return [f"expert {domain_name} professional specialist"]
    
    def score_candidate_batch_for_domain(
        self, 
        candidates: List[CandidateProfile], 
        job_category: str
    ) -> Dict[str, float]:
        """
        Score multiple candidates for domain fit in a single GPT call for efficiency.
        
        Args:
            candidates: List of candidates to evaluate
            job_category: Target job category
            
        Returns:
            Dictionary mapping candidate_id to relevance_score
        """
        if not candidates:
            return {}
        
        domain_name = job_category.replace("_", " ").replace(".yml", "")
        
        # Create batch prompt with all candidates
        candidates_text = ""
        for i, candidate in enumerate(candidates, 1):
            candidates_text += f"""
        {i}. ID: {candidate.id}
           Name: {candidate.name}
           Summary: {candidate.summary or 'No summary available'}
        """
        
        prompt = f"""
        Score how well each candidate fits the role: {domain_name}
        
        Rate each candidate from 0.0 to 1.0:
        - 1.0 = Perfect domain match, clearly belongs in this field
        - 0.8 = Good match, strong relevant background  
        - 0.6 = Moderate match, some relevant experience
        - 0.4 = Weak match, limited relevance
        - 0.2 = Poor match, minimal connection
        - 0.0 = No match, clearly wrong domain
        
        Candidates:
        {candidates_text}
        
        Focus on:
        - Specific domain expertise and education
        - Relevant professional experience
        - Field-specific skills and knowledge
        - Avoiding cross-domain false matches
        
        Return JSON with candidate ID as key and score as value:
        {{
            "{candidates[0].id if candidates else 'example_id'}": 0.85,
            "another_id": 0.92,
            ...
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert recruiter with deep knowledge across all professional domains. Score candidates based on genuine domain expertise, not superficial keyword matches."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            scores = json.loads(result_text)
            
            # Ensure all candidates have scores
            result = {}
            for candidate in candidates:
                score = scores.get(candidate.id, 0.5)  # Default to neutral if missing
                result[candidate.id] = max(0.0, min(1.0, float(score)))
            
            return result
            
        except Exception as e:
            logger.error(f"Batch scoring failed: {e}")
            # Return neutral scores for all candidates on failure
            return {candidate.id: 0.5 for candidate in candidates}


# Global GPT service instance
gpt_service = GPTService() 