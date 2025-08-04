#!/usr/bin/env python3
"""
Filter Extraction Service
========================

Extracts filters from user queries and applies them to hybrid search
for improved performance and relevance.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from ..services.gpt_service import gpt_service
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class QueryFilters:
    """Extracted filters from user query."""
    location_filters: List[str] = None
    experience_filters: List[str] = None
    skill_filters: List[str] = None
    education_filters: List[str] = None
    industry_filters: List[str] = None
    title_filters: List[str] = None
    exclude_filters: List[str] = None
    
    def __post_init__(self):
        if self.location_filters is None:
            self.location_filters = []
        if self.experience_filters is None:
            self.experience_filters = []
        if self.skill_filters is None:
            self.skill_filters = []
        if self.education_filters is None:
            self.education_filters = []
        if self.industry_filters is None:
            self.industry_filters = []
        if self.title_filters is None:
            self.title_filters = []
        if self.exclude_filters is None:
            self.exclude_filters = []

class FilterExtractionService:
    """Service for extracting filters from user queries."""
    
    def __init__(self):
        # Common filter patterns
        self.location_patterns = [
            r'in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'from\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'based\s+in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'located\s+in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'remote\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'at\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'near\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'around\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
        ]
        
        self.experience_patterns = [
            r'(\d+)\s+years?\s+experience',
            r'(\d+)\+?\s+years?\s+of\s+experience',
            r'experienced\s+([A-Za-z\s]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'senior\s+([A-Za-z\s]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'junior\s+([A-Za-z\s]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'entry\s+level\s+([A-Za-z\s]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
        ]
        
        self.skill_patterns = [
            r'with\s+([A-Za-z\s,]+?)\s+skills?',
            r'knowing\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'expertise\s+in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'proficient\s+in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'experience\s+with\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'using\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'familiar\s+with\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'knowledge\s+of\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'background\s+in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
        ]
        
        self.education_patterns = [
            r'phd\s+in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'master\s+in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'bachelor\s+in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'degree\s+in\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'graduated\s+from\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
        ]
        
        self.exclude_patterns = [
            r'not\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'exclude\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'without\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
            r'no\s+([A-Za-z\s,]+?)(?:\s+with|\s+who|\s+and|\s+or|$)',
        ]
    
    def extract_filters(self, query: str) -> QueryFilters:
        """
        Extract filters from user query using both pattern matching and GPT.
        
        Args:
            query: User's search query
            
        Returns:
            QueryFilters object with extracted filters
        """
        # First, use pattern matching for quick extraction
        pattern_filters = self._extract_pattern_filters(query)
        
        # Then, use GPT for more sophisticated extraction
        gpt_filters = self._extract_gpt_filters(query)
        
        # Combine both approaches
        combined_filters = self._combine_filters(pattern_filters, gpt_filters)
        
        logger.info(f"Extracted filters from query '{query}': {combined_filters}")
        return combined_filters
    
    def _extract_pattern_filters(self, query: str) -> QueryFilters:
        """Extract filters using regex patterns."""
        query_lower = query.lower()
        filters = QueryFilters()
        
        # Extract location filters
        for pattern in self.location_patterns:
            matches = re.findall(pattern, query_lower)
            filters.location_filters.extend([match.strip() for match in matches])
        
        # Extract experience filters
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, query_lower)
            filters.experience_filters.extend([match.strip() for match in matches])
        
        # Extract skill filters
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, query_lower)
            filters.skill_filters.extend([match.strip() for match in matches])
        
        # Extract education filters
        for pattern in self.education_patterns:
            matches = re.findall(pattern, query_lower)
            filters.education_filters.extend([match.strip() for match in matches])
        
        # Extract exclude filters
        for pattern in self.exclude_patterns:
            matches = re.findall(pattern, query_lower)
            filters.exclude_filters.extend([match.strip() for match in matches])
        
        return filters
    
    def _extract_gpt_filters(self, query: str) -> QueryFilters:
        """Extract filters using GPT for more sophisticated analysis."""
        if not gpt_service.is_available():
            return QueryFilters()
        
        try:
            gpt_prompt = f"""Extract filters from this search query: "{query}"

Analyze the query carefully and extract ALL relevant filters. Be thorough and include:
- location_filters: Cities, states, countries, remote work preferences
- experience_filters: Years of experience, seniority levels (junior, senior, lead, etc.)
- skill_filters: Technical skills, programming languages, tools, technologies
- education_filters: Degree requirements, universities, certifications
- industry_filters: Industry preferences (healthcare, finance, tech, etc.)
- title_filters: Job title preferences or requirements
- exclude_filters: Things to exclude or avoid

IMPORTANT GUIDELINES:
1. Extract ALL mentioned filters, even if they seem obvious
2. For skills, include both specific technologies (Python, AWS) and general skills (leadership, communication)
3. For experience, include both years (5+ years) and levels (senior, junior)
4. For locations, include both specific places and general preferences (remote, onsite)
5. For industries, extract any mentioned industry context
6. Be comprehensive - better to include too many filters than miss important ones

Return a JSON object with these filter categories:
{{
  "location_filters": ["list of locations"],
  "experience_filters": ["list of experience requirements"],
  "skill_filters": ["list of skills and technologies"],
  "education_filters": ["list of education requirements"],
  "industry_filters": ["list of industry preferences"],
  "title_filters": ["list of title preferences"],
  "exclude_filters": ["list of exclusions"]
}}

Return only the JSON object:"""

            response = gpt_service._make_gpt_request(
                [{"role": "user", "content": gpt_prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            gpt_data = json.loads(response)
            return QueryFilters(
                location_filters=gpt_data.get('location_filters', []),
                experience_filters=gpt_data.get('experience_filters', []),
                skill_filters=gpt_data.get('skill_filters', []),
                education_filters=gpt_data.get('education_filters', []),
                industry_filters=gpt_data.get('industry_filters', []),
                title_filters=gpt_data.get('title_filters', []),
                exclude_filters=gpt_data.get('exclude_filters', [])
            )
            
        except Exception as e:
            logger.warning(f"GPT filter extraction failed: {e}")
            return QueryFilters()
    
    def _combine_filters(self, pattern_filters: QueryFilters, gpt_filters: QueryFilters) -> QueryFilters:
        """Combine filters from pattern matching and GPT."""
        combined = QueryFilters()
        
        # Combine location filters
        combined.location_filters = list(set(pattern_filters.location_filters + gpt_filters.location_filters))
        
        # Combine experience filters
        combined.experience_filters = list(set(pattern_filters.experience_filters + gpt_filters.experience_filters))
        
        # Combine skill filters
        combined.skill_filters = list(set(pattern_filters.skill_filters + gpt_filters.skill_filters))
        
        # Combine education filters
        combined.education_filters = list(set(pattern_filters.education_filters + gpt_filters.education_filters))
        
        # Combine industry filters
        combined.industry_filters = list(set(pattern_filters.industry_filters + gpt_filters.industry_filters))
        
        # Combine title filters
        combined.title_filters = list(set(pattern_filters.title_filters + gpt_filters.title_filters))
        
        # Combine exclude filters
        combined.exclude_filters = list(set(pattern_filters.exclude_filters + gpt_filters.exclude_filters))
        
        return combined
    
    def apply_filters_to_search(self, filters: QueryFilters, search_config: Dict) -> Dict:
        """
        Apply extracted filters to search configuration.
        
        Args:
            filters: Extracted query filters
            search_config: Current search configuration
            
        Returns:
            Enhanced search configuration with filters applied
        """
        enhanced_config = search_config.copy()
        
        # Add location filters to vector search
        if filters.location_filters:
            enhanced_config['location_keywords'] = filters.location_filters
        
        # Add skill filters to BM25 search
        if filters.skill_filters:
            enhanced_config['skill_keywords'] = filters.skill_filters
        
        # Add experience filters
        if filters.experience_filters:
            enhanced_config['experience_keywords'] = filters.experience_filters
        
        # Add education filters
        if filters.education_filters:
            enhanced_config['education_keywords'] = filters.education_filters
        
        # Add exclude filters
        if filters.exclude_filters:
            enhanced_config['exclude_keywords'] = filters.exclude_filters
        
        return enhanced_config
    
    def create_enhanced_query(self, original_query: str, filters: QueryFilters) -> str:
        """
        Create an enhanced query with extracted filters.
        
        Args:
            original_query: Original user query
            filters: Extracted filters
            
        Returns:
            Enhanced query string
        """
        enhanced_parts = [original_query]
        
        if filters.skill_filters:
            enhanced_parts.append(f"skills: {', '.join(filters.skill_filters)}")
        
        if filters.experience_filters:
            enhanced_parts.append(f"experience: {', '.join(filters.experience_filters)}")
        
        if filters.location_filters:
            enhanced_parts.append(f"location: {', '.join(filters.location_filters)}")
        
        if filters.education_filters:
            enhanced_parts.append(f"education: {', '.join(filters.education_filters)}")
        
        return " | ".join(enhanced_parts)

# Global instance
filter_extraction_service = FilterExtractionService() 