"""Enhanced data models for candidates with additional search fields."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


@dataclass
class CandidateProfile:
    """Enhanced candidate profile with additional search-relevant information."""
    id: str
    name: str
    email: Optional[str] = None
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    # Enhanced search fields
    headline: Optional[str] = None
    experience_text: Optional[str] = None
    skills_text: Optional[str] = None
    education_text: Optional[str] = None
    awards_certifications: Optional[str] = None
    country: Optional[str] = None
    years_experience: Optional[int] = None
    prestige_score: Optional[int] = None
    comprehensive_summary: Optional[str] = None
    
    def __str__(self) -> str:
        return f"Candidate({self.id}, {self.name})"
    
    def get_searchable_text(self) -> str:
        """Get all searchable text combined for keyword matching."""
        text_fields = [
            self.name or "",
            self.summary or "",
            self.headline or "",
            self.experience_text or "",
            self.skills_text or "",
            self.education_text or "",
            self.awards_certifications or "",
            self.comprehensive_summary or ""
        ]
        return " ".join([field for field in text_fields if field]).lower()
    
    def has_keyword(self, keyword: str) -> bool:
        """Check if candidate profile contains a specific keyword."""
        search_text = self.get_searchable_text()
        return keyword.lower() in search_text
    
    def satisfies_hard_filters(self, must_have: List[str], exclude: List[str]) -> bool:
        """Check if candidate satisfies hard filter requirements."""
        search_text = self.get_searchable_text()
        
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
        
        search_text = self.get_searchable_text()
        
        # Count matches and calculate weighted score
        matches = 0
        for keyword in preferred_keywords:
            if keyword.lower() in search_text:
                matches += 1
        
        # Return score as percentage of preferred keywords matched
        return matches / len(preferred_keywords) if preferred_keywords else 0.0
    
    def calculate_experience_score(self, target_years: Optional[int] = None) -> float:
        """Calculate experience-based score."""
        if not self.years_experience or not target_years:
            return 0.0
        
        # Score based on proximity to target years
        diff = abs(self.years_experience - target_years)
        # Normalize: closer to target = higher score
        return max(0.0, 1.0 - (diff / max(target_years, 10)))
    
    def get_skills_list(self) -> List[str]:
        """Extract individual skills from skills text."""
        if not self.skills_text:
            return []
        return [skill.strip() for skill in self.skills_text.split(",") if skill.strip()]
    
    def get_experience_keywords(self) -> List[str]:
        """Extract key experience terms."""
        if not self.experience_text:
            return []
        
        # Simple keyword extraction from experience
        import re
        # Extract company names and job titles (simplified approach)
        keywords = []
        if " at " in self.experience_text:
            parts = self.experience_text.split(" | ")
            for part in parts:
                if " at " in part:
                    title_company = part.split(" at ")
                    if len(title_company) >= 2:
                        title = title_company[0].strip()
                        company = title_company[1].split(".")[0].strip()
                        keywords.extend([title, company])
        
        return [kw for kw in keywords if len(kw) > 2]  # Filter out very short terms


@dataclass
class SearchResult:
    """Represents a search result with score and metadata."""
    candidate: CandidateProfile
    score: float
    source: str  # e.g., "vector", "bm25", "hybrid"
    rank: int
    breakdown: Optional[Dict[str, float]] = None  # Score breakdown for debugging
    
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
    ENHANCED_HYBRID = "enhanced_hybrid"  # New strategy using additional fields


@dataclass
class SearchQuery:
    """Enhanced search query with additional filtering options."""
    query_text: str
    job_category: str
    strategy: SearchStrategy
    max_candidates: int = 100
    
    # Enhanced filtering options
    required_skills: Optional[List[str]] = None
    min_years_experience: Optional[int] = None
    max_years_experience: Optional[int] = None
    required_education_level: Optional[str] = None
    preferred_countries: Optional[List[str]] = None
    exclude_keywords: Optional[List[str]] = None
    
    def get_category_name(self) -> str:
        """Extract clean category name from job category."""
        return self.job_category.replace("_", " ").replace(".yml", "")


@dataclass
class CandidateScores:
    """Enhanced aggregated scores for a candidate from multiple search strategies."""
    candidate_id: str
    vector_score: float = 0.0
    bm25_score: float = 0.0
    gpt_score: float = 0.0
    soft_filter_score: float = 0.0
    experience_score: float = 0.0
    skills_score: float = 0.0
    education_score: float = 0.0
    prestige_score: float = 0.0
    combined_score: float = 0.0
    
    def calculate_enhanced_score(
        self, 
        vector_weight: float = 0.4, 
        bm25_weight: float = 0.3, 
        soft_filter_weight: float = 0.1,
        experience_weight: float = 0.1,
        skills_weight: float = 0.05,
        education_weight: float = 0.03,
        prestige_weight: float = 0.02
    ) -> float:
        """Calculate weighted combined score including all enhancement factors."""
        # Normalize weights to sum to 1
        total_weight = (vector_weight + bm25_weight + soft_filter_weight + 
                       experience_weight + skills_weight + education_weight + prestige_weight)
        
        vector_weight = vector_weight / total_weight
        bm25_weight = bm25_weight / total_weight
        soft_filter_weight = soft_filter_weight / total_weight
        experience_weight = experience_weight / total_weight
        skills_weight = skills_weight / total_weight
        education_weight = education_weight / total_weight
        prestige_weight = prestige_weight / total_weight
        
        self.combined_score = (
            self.vector_score * vector_weight + 
            self.bm25_score * bm25_weight +
            self.soft_filter_score * soft_filter_weight +
            self.experience_score * experience_weight +
            self.skills_score * skills_weight +
            self.education_score * education_weight +
            self.prestige_score * prestige_weight
        )
        return self.combined_score
    
    def get_score_breakdown(self) -> Dict[str, float]:
        """Get detailed breakdown of all score components."""
        return {
            "vector_score": self.vector_score,
            "bm25_score": self.bm25_score,
            "gpt_score": self.gpt_score,
            "soft_filter_score": self.soft_filter_score,
            "experience_score": self.experience_score,
            "skills_score": self.skills_score,
            "education_score": self.education_score,
            "prestige_score": self.prestige_score,
            "combined_score": self.combined_score
        }
    
    def __str__(self) -> str:
        return f"CandidateScores({self.candidate_id}, combined={self.combined_score:.3f})"


@dataclass
class SearchConfig:
    """Enhanced search configuration with additional parameters."""
    strategy: SearchStrategy
    max_candidates: int
    vector_weight: float
    bm25_weight: float
    soft_filter_weight: float = 0.1
    experience_weight: float = 0.1
    skills_weight: float = 0.05
    education_weight: float = 0.03
    prestige_weight: float = 0.02
    
    # Field-specific search weights
    headline_search_weight: float = 1.5
    experience_search_weight: float = 1.3
    skills_search_weight: float = 1.2
    education_search_weight: float = 1.1
    awards_search_weight: float = 1.0 