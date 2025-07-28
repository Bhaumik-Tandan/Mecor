"""Configuration settings for the search agent application."""

import os
from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


@dataclass
class APIConfig:
    """API configuration settings."""
    voyage_api_key: str
    turbopuffer_api_key: str
    openai_api_key: str
    eval_endpoint: str
    user_email: str
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Create APIConfig from environment variables."""
        return cls(
            voyage_api_key=os.getenv('VOYAGE_API_KEY', ''),
            turbopuffer_api_key=os.getenv('TURBOPUFFER_API_KEY', ''),
            openai_api_key=os.getenv('OPENAI_API_KEY', ''),
            eval_endpoint=os.getenv('EVAL_ENDPOINT', 'https://mercor-dev--search-eng-interview.modal.run/evaluate'),
            user_email=os.getenv('USER_EMAIL', '')
        )


@dataclass
class TurbopufferConfig:
    """Turbopuffer configuration settings."""
    region: str
    namespace: str
    
    @classmethod
    def from_env(cls) -> 'TurbopufferConfig':
        """Create TurbopufferConfig from environment variables."""
        return cls(
            region=os.getenv('TURBOPUFFER_REGION', 'aws-us-west-2'),
            namespace=os.getenv('TURBOPUFFER_NAMESPACE', 'default_namespace')
        )


@dataclass
class SearchConfig:
    """Search configuration settings."""
    max_candidates_per_query: int
    top_k_results: int
    max_retries: int
    request_timeout: int
    thread_pool_size: int
    vector_search_weight: float
    bm25_search_weight: float
    soft_filter_weight: float
    
    @classmethod
    def from_env(cls) -> 'SearchConfig':
        """Create SearchConfig from environment variables."""
        return cls(
            max_candidates_per_query=int(os.getenv('MAX_CANDIDATES_PER_QUERY', '200')),
            top_k_results=int(os.getenv('TOP_K_RESULTS', '100')),
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', '30')),
            thread_pool_size=int(os.getenv('THREAD_POOL_SIZE', '5')),
            vector_search_weight=float(os.getenv('VECTOR_SEARCH_WEIGHT', '0.6')),
            bm25_search_weight=float(os.getenv('BM25_SEARCH_WEIGHT', '0.4')),
            soft_filter_weight=float(os.getenv('SOFT_FILTER_WEIGHT', '0.2'))
        )


@dataclass
class ApplicationConfig:
    """Main application configuration."""
    api: APIConfig
    turbopuffer: TurbopufferConfig
    search: SearchConfig
    
    # Job categories to evaluate
    job_categories: List[str] = None
    
    def __post_init__(self):
        if self.job_categories is None:
            self.job_categories = [
                "tax_lawyer.yml",
                "junior_corporate_lawyer.yml",
                "radiology.yml", 
                "doctors_md.yml",
                "biology_expert.yml",
                "anthropology.yml",
                "mathematics_phd.yml",
                "quantitative_finance.yml",
                "bankers.yml",
                "mechanical_engineers.yml"
            ]
    
    @classmethod
    def load(cls) -> 'ApplicationConfig':
        """Load configuration from environment variables."""
        return cls(
            api=APIConfig.from_env(),
            turbopuffer=TurbopufferConfig.from_env(),
            search=SearchConfig.from_env()
        )


# Global configuration instance
config = ApplicationConfig.load() 