"""Data models for candidates and search results."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


@dataclass
class CandidateProfile:
    """Represents a candidate profile with all relevant information."""
    id: str
    name: str
    email: Optional[str] = None
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    def __str__(self) -> str:
        return f"Candidate({self.id}, {self.name})"
    
    def has_keyword(self, keyword: str) -> bool:
        """Check if candidate profile contains a specific keyword."""
        search_text = f"{self.name} {self.summary or ''}".lower()
        return keyword.lower() in search_text
    
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
    combined_score: float = 0.0
    
    def calculate_combined_score(self, vector_weight: float = 0.6, bm25_weight: float = 0.4) -> float:
        """Calculate weighted combined score."""
        self.combined_score = (self.vector_score * vector_weight + 
                             self.bm25_score * bm25_weight)
        return self.combined_score
    
    def __str__(self) -> str:
        return f"CandidateScores({self.candidate_id}, combined={self.combined_score:.3f})" 