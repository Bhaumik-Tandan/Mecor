"""Data models for candidates and search results."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import re


@dataclass
class CandidateProfile:
    """Represents a candidate profile with all relevant information."""
    id: str
    name: str
    email: Optional[str] = None
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    linkedin_id: Optional[str] = None
    country: Optional[str] = None
    experience_years: Optional[int] = None
    
    def __str__(self) -> str:
        return f"Candidate({self.id}, {self.name})"
    
    def has_keyword(self, keyword: str) -> bool:
        """Check if candidate profile contains a specific keyword."""
        search_text = f"{self.name} {self.summary or ''}".lower()
        return keyword.lower() in search_text
    
    def is_linkedin_valid(self) -> bool:
        """Validate LinkedIn profile completeness."""
        if not self.linkedin_url and not self.linkedin_id:
            return False
        
        if self.linkedin_url:
            # Check if LinkedIn URL format is valid
            linkedin_pattern = r'https?://(www\.)?linkedin\.com/in/[\w\-]+'
            return bool(re.match(linkedin_pattern, self.linkedin_url))
        
        return bool(self.linkedin_id)
    
    def estimate_experience_years(self) -> int:
        """Estimate years of experience from summary text."""
        if self.experience_years:
            return self.experience_years
        
        if not self.summary:
            return 0
        
        summary_lower = self.summary.lower()
        
        # Look for explicit year mentions
        year_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|exp)',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?(?:experience|exp)',
            r'over\s+(\d+)\s+years?',
            r'more\s+than\s+(\d+)\s+years?',
            r'(\d+)\+\s*years?'
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, summary_lower)
            if matches:
                try:
                    return max(int(match) for match in matches)
                except ValueError:
                    continue
        
        # Rough estimation based on career progression keywords
        if any(word in summary_lower for word in ['senior', 'lead', 'principal', 'director']):
            return 8
        elif any(word in summary_lower for word in ['manager', 'supervisor']):
            return 6
        elif any(word in summary_lower for word in ['specialist', 'analyst']):
            return 4
        elif any(word in summary_lower for word in ['junior', 'associate', 'intern']):
            return 2
        
        return 3  # Default assumption
    
    def satisfies_hard_filters(self, must_have: List[str], exclude: List[str]) -> bool:
        """Check if candidate satisfies hard filter requirements."""
        search_text = f"{self.name} {self.summary or ''}".lower()
        
        # Check must-have requirements
        for requirement in must_have:
            if requirement.lower() not in search_text:
                return False
        
        # Check exclusion criteria
        for exclusion in exclude:
            if exclusion.lower() in search_text:
                return False
        
        return True
    
    def calculate_soft_filter_score(self, preferred_keywords: List[str]) -> float:
        """Calculate soft filter boost score based on preferred keywords."""
        if not preferred_keywords:
            return 0.0
        
        search_text = f"{self.name} {self.summary or ''}".lower()
        
        # Count matches and calculate weighted score
        matches = 0
        for keyword in preferred_keywords:
            if keyword.lower() in search_text:
                matches += 1
        
        # Calculate percentage and scale to 0-1
        base_score = matches / len(preferred_keywords)
        
        # Apply bonus for LinkedIn profile completeness
        linkedin_bonus = 0.1 if self.is_linkedin_valid() else 0.0
        
        # Apply experience bonus for relevant roles
        experience_bonus = min(0.1, self.estimate_experience_years() / 100.0)
        
        return min(1.0, base_score + linkedin_bonus + experience_bonus)
    
    def calculate_quality_score(self) -> float:
        """Calculate overall candidate quality score."""
        score = 0.0
        
        # LinkedIn completeness (30%)
        if self.is_linkedin_valid():
            score += 0.3
        
        # Profile completeness (20%)
        completeness_factors = [
            bool(self.name),
            bool(self.email),
            bool(self.summary and len(self.summary) > 50),
            bool(self.country)
        ]
        score += 0.2 * (sum(completeness_factors) / len(completeness_factors))
        
        # Experience relevance (30%)
        exp_years = self.estimate_experience_years()
        if exp_years >= 2:
            score += 0.3 * min(1.0, exp_years / 10.0)
        
        # Summary quality (20%)
        if self.summary:
            summary_len = len(self.summary)
            if summary_len > 100:
                score += 0.2 * min(1.0, summary_len / 500.0)
        
        return min(1.0, score)


@dataclass
class SearchResult:
    """Represents a search result with score and metadata."""
    candidate: CandidateProfile
    score: float
    source: str  # e.g., "vector", "bm25", "hybrid"
    rank: int
    
    def __str__(self) -> str:
        return f"SearchResult({self.candidate.id}, score={self.score:.3f}, rank={self.rank})"


@dataclass
class EvaluationResult:
    """Represents the result of candidate evaluation."""
    config_name: str
    num_candidates: int
    average_final_score: float
    individual_results: List[Dict[str, Any]]
    average_soft_scores: List[Dict[str, Any]]
    average_hard_scores: List[Dict[str, Any]]
    
    def __str__(self) -> str:
        return f"EvaluationResult({self.config_name}, score={self.average_final_score:.2f})"


class SearchStrategy(Enum):
    """Enumeration of available search strategies."""
    VECTOR_ONLY = "vector_only"
    BM25_ONLY = "bm25_only"
    HYBRID = "hybrid"
    GPT_ENHANCED = "gpt_enhanced"


@dataclass
class SearchQuery:
    """Represents a search query with metadata."""
    query_text: str
    job_category: str
    strategy: SearchStrategy
    max_candidates: int = 100
    
    def get_category_name(self) -> str:
        """Extract clean category name from job category."""
        return self.job_category.replace("_", " ").replace(".yml", "")


@dataclass
class CandidateScores:
    """Aggregated scores for a candidate from multiple search strategies."""
    candidate_id: str
    vector_score: float = 0.0
    bm25_score: float = 0.0
    gpt_score: float = 0.0
    soft_filter_score: float = 0.0
    combined_score: float = 0.0
    
    def calculate_combined_score(
        self, 
        vector_weight: float = 0.6, 
        bm25_weight: float = 0.4, 
        soft_filter_weight: float = 0.2
    ) -> float:
        """Calculate weighted combined score including soft filter boost."""
        # Normalize weights to sum to 1
        total_weight = vector_weight + bm25_weight + soft_filter_weight
        vector_weight = vector_weight / total_weight
        bm25_weight = bm25_weight / total_weight
        soft_filter_weight = soft_filter_weight / total_weight
        
        self.combined_score = (
            self.vector_score * vector_weight + 
            self.bm25_score * bm25_weight +
            self.soft_filter_score * soft_filter_weight
        )
        return self.combined_score
    
    def __str__(self) -> str:
        return f"CandidateScores({self.candidate_id}, combined={self.combined_score:.3f}, soft={self.soft_filter_score:.3f})" 