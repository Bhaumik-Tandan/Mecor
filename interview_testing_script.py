#!/usr/bin/env python3
"""
Simple Interview Testing Script for Mercor Search Agent
======================================================

This script simply asks for a query and returns quality results.
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import traceback

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from src.services.search_service import search_service
from src.utils.logger import get_logger, setup_logger
from src.utils.helpers import PerformanceTimer, save_json_file

# Setup logging
logger = setup_logger(
    name="interview_testing",
    level="INFO",
    log_file="logs/interview_testing.log"
)

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_candidates_table(candidates_data: Dict[str, List], max_display: int = 10):
    """Print candidates in a pretty tabular format with colors."""
    if not candidates_data.get('candidate_ids'):
        print(f"{Colors.YELLOW}No candidates found{Colors.END}")
        return
    
    ids = candidates_data['candidate_ids'][:max_display]
    names = candidates_data['candidate_names'][:max_display]
    countries = candidates_data['candidate_countries'][:max_display]
    summaries = candidates_data['candidate_summaries'][:max_display]
    
    # Calculate column widths
    max_id_len = max(len(str(id)) for id in ids) if ids else 10
    max_name_len = max(len(str(name)) for name in names) if names else 20
    max_country_len = max(len(str(country)) for country in countries) if countries else 15
    max_summary_len = 50  # Limit summary display
    
    # Ensure minimum widths
    max_id_len = max(max_id_len, 8)
    max_name_len = max(max_name_len, 15)
    max_country_len = max(max_country_len, 10)
    
    # Print header
    header = f"{Colors.BOLD}{Colors.HEADER}"
    header += f"{'ID':<{max_id_len}} | "
    header += f"{'Name':<{max_name_len}} | "
    header += f"{'Country':<{max_country_len}} | "
    header += f"{'Summary':<{max_summary_len}}"
    header += f"{Colors.END}"
    print(header)
    
    # Print separator
    separator = f"{Colors.CYAN}{'=' * (max_id_len + max_name_len + max_country_len + max_summary_len + 9)}{Colors.END}"
    print(separator)
    
    # Print candidate rows
    for i, (candidate_id, name, country, summary) in enumerate(zip(ids, names, countries, summaries)):
        # Truncate summary if too long
        summary_display = str(summary)[:max_summary_len-3] + "..." if summary and len(str(summary)) > max_summary_len else str(summary) or "N/A"
        
        # Alternate row colors
        row_color = Colors.GREEN if i % 2 == 0 else Colors.BLUE
        
        row = f"{row_color}"
        row += f"{candidate_id:<{max_id_len}} | "
        row += f"{name:<{max_name_len}} | "
        row += f"{country:<{max_country_len}} | "
        row += f"{summary_display:<{max_summary_len}}"
        row += f"{Colors.END}"
        print(row)
    
    # Show total count
    total_candidates = len(candidates_data['candidate_ids'])
    if total_candidates > max_display:
        print(f"\n{Colors.YELLOW}Showing {max_display} of {total_candidates} candidates{Colors.END}")

class SimpleSearchAgent:
    """Simple search agent that just asks for a query and returns results."""
    
    def __init__(self):
        self.search_service = search_service
        logger.info("🚀 Initialized Simple Search Agent")
    
    def search(self, query_text: str) -> Dict[str, Any]:
        """Simple search function that returns quality results."""
        start_time = time.time()
        
        print(f"{Colors.CYAN}🔍 Searching for: {query_text}{Colors.END}")
        
        try:
            # Use GPT-enhanced search
                search_query = SearchQuery(
                    query_text=query_text,
                job_category="general",
                strategy=SearchStrategy.GPT_ENHANCED,
                max_candidates=20
                )
                
                candidates = self.search_service.search_candidates(
                    search_query, 
                SearchStrategy.GPT_ENHANCED
            )
            
            # Apply quality filtering
            quality_candidates = self._filter_by_quality(candidates)
            
            # Adjust count based on quality
            final_candidates = self._adjust_count(quality_candidates)
            
            search_time = time.time() - start_time
            
            result = {
                "num_candidates": len(final_candidates),
                "candidate_ids": [c.id for c in final_candidates],
                "candidate_names": [c.name for c in final_candidates],
                "candidate_summaries": [c.summary for c in final_candidates],
                "candidate_countries": [c.country for c in final_candidates],
                "search_time": search_time
            }
            
            print(f"{Colors.GREEN}✅ Found {len(final_candidates)} quality candidates in {search_time:.2f}s{Colors.END}")
            
            return result
            
        except Exception as e:
            print(f"{Colors.RED}❌ Search failed: {e}{Colors.END}")
            return {"num_candidates": 0, "candidate_ids": [], "candidate_names": [], "candidate_summaries": [], "candidate_countries": [], "search_time": 0}
    
    def _filter_by_quality(self, candidates: List[CandidateProfile]) -> List[CandidateProfile]:
        """Filter candidates by quality."""
        if not candidates:
            return []
        
        quality_candidates = []
        for candidate in candidates:
            quality_score = self._calculate_quality_score(candidate)
            if quality_score >= 0.4:  # Minimum quality threshold
                quality_candidates.append(candidate)
        
        # Sort by quality score
        quality_candidates.sort(key=lambda c: self._calculate_quality_score(c), reverse=True)
        
        return quality_candidates
    
    def _calculate_quality_score(self, candidate: CandidateProfile) -> float:
        """Calculate quality score for a candidate."""
        score = 0.0
        
        # Summary completeness (40% weight)
        if candidate.summary:
            summary_length = len(candidate.summary.strip())
            if summary_length > 200:
                score += 0.4
            elif summary_length > 100:
                score += 0.3
            elif summary_length > 50:
                score += 0.2
            else:
                score += 0.1
        
        # Name completeness (30% weight)
        if candidate.name and len(candidate.name.strip()) > 2:
            score += 0.3
        
        # Country information (15% weight)
        if candidate.country and candidate.country.strip():
            score += 0.15
        
        # LinkedIn ID presence (15% weight)
        if candidate.linkedin_id and candidate.linkedin_id.strip():
            score += 0.15
        
        return min(score, 1.0)
    
    def _adjust_count(self, candidates: List[CandidateProfile]) -> List[CandidateProfile]:
        """Adjust candidate count based on quality."""
        if not candidates:
            return []
        
        # Count high-quality candidates
        high_quality_count = sum(1 for c in candidates if self._calculate_quality_score(c) >= 0.7)
        
        # Return fewer candidates if quality is high
        if high_quality_count >= 5:
            return candidates[:10]
        elif high_quality_count >= 3:
            return candidates[:15]
        else:
            return candidates[:20]

def main():
    """Simple main function that asks for a query and shows results."""
    print(f"{Colors.BOLD}{Colors.HEADER}🚀 Simple Mercor Search{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 40}{Colors.END}")
    
    try:
        agent = SimpleSearchAgent()
        
        while True:
            # Ask for query
            query = input(f"\n{Colors.BLUE}Enter your search query (or 'quit' to exit): {Colors.END}")
            
            if query.lower() in ['quit', 'exit', 'q']:
                print(f"{Colors.YELLOW}Goodbye!{Colors.END}")
                break
            
            if not query.strip():
                print(f"{Colors.YELLOW}Please enter a valid query.{Colors.END}")
                continue
            
            # Search and display results
            result = agent.search(query.strip())
            
            if result["num_candidates"] > 0:
                print(f"\n{Colors.BOLD}📋 Results:{Colors.END}")
                print_candidates_table(result)
            else:
                print(f"{Colors.YELLOW}No candidates found.{Colors.END}")
            
            print(f"\n{Colors.CYAN}{'=' * 40}{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Goodbye!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")

if __name__ == "__main__":
    main() 