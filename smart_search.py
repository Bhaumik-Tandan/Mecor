#!/usr/bin/env python3
"""
Smart Search Interface - Simple Interactive Search with Format Detection
=======================================================================

This is a simple interface that:
1. Asks for your query
2. Automatically detects the best format using GPT
3. Returns results in the optimal format
4. Runs continuous improvement in the background
"""

import asyncio
import json
import time
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from src.services.search_service import search_service
from src.services.gpt_service import gpt_service
from src.utils.logger import get_logger, setup_logger

# Setup logging
logger = setup_logger(
    name="smart_search",
    level="INFO",
    log_file="logs/smart_search.log"
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

class SmartSearch:
    """Smart search with automatic format detection."""
    
    def __init__(self):
        self.search_service = search_service
        self.gpt_service = gpt_service
        logger.info("🚀 Smart Search initialized")
    
    def detect_format(self, query: str) -> str:
        """Detect the best format for the query using GPT."""
        if not self.gpt_service.is_available():
            return 'table'  # Default fallback
        
        try:
            prompt = f"""Analyze this search query and determine the best output format:

Query: "{query}"

Available formats:
- json: For API integration, data processing, programmatic use
- csv: For spreadsheet analysis, data export, bulk processing  
- table: For human-readable display, quick overview, presentation
- summary: For brief overview, executive summary, high-level insights

Consider user intent and likely use case. Return ONLY: json, csv, table, or summary"""

            response = self.gpt_service._make_gpt_request(
                [{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            detected_format = response.strip().lower()
            if detected_format in ['json', 'csv', 'table', 'summary']:
                return detected_format
            
        except Exception as e:
            logger.warning(f"GPT format detection failed: {e}")
        
        return 'table'  # Default fallback
    
    def search(self, query: str) -> Dict[str, Any]:
        """Perform smart search with automatic format detection."""
        start_time = time.time()
        
        print(f"{Colors.CYAN}🔍 Searching for: {query}{Colors.END}")
        
        try:
            # Detect format
            detected_format = self.detect_format(query)
            print(f"{Colors.BLUE}📊 Detected format: {detected_format}{Colors.END}")
            
            # Perform search
            search_query = SearchQuery(
                query_text=query,
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
            final_candidates = self._adjust_count(quality_candidates)
            
            search_time = time.time() - start_time
            
            # Format results
            formatted_results = self._format_results(final_candidates, detected_format)
            
            result = {
                'query': query,
                'format': detected_format,
                'candidates': final_candidates,
                'formatted_results': formatted_results,
                'search_time': search_time,
                'candidate_count': len(final_candidates),
                'quality_score': self._calculate_average_quality(final_candidates),
                'gpt_enhanced': gpt_service.is_available()
            }
            
            print(f"{Colors.GREEN}✅ Found {len(final_candidates)} quality candidates in {search_time:.2f}s{Colors.END}")
            
            return result
            
        except Exception as e:
            print(f"{Colors.RED}❌ Search failed: {e}{Colors.END}")
            return {
                'query': query,
                'format': 'table',
                'candidates': [],
                'formatted_results': {'error': str(e)},
                'search_time': time.time() - start_time,
                'candidate_count': 0,
                'quality_score': 0.0,
                'gpt_enhanced': False
            }
    
    def _filter_by_quality(self, candidates: List[CandidateProfile]) -> List[CandidateProfile]:
        """Filter candidates by quality."""
        if not candidates:
            return []
        
        quality_candidates = []
        for candidate in candidates:
            quality_score = self._calculate_quality_score(candidate)
            if quality_score >= 0.4:
                quality_candidates.append(candidate)
        
        quality_candidates.sort(key=lambda c: self._calculate_quality_score(c), reverse=True)
        return quality_candidates
    
    def _adjust_count(self, candidates: List[CandidateProfile]) -> List[CandidateProfile]:
        """Adjust candidate count based on quality."""
        if not candidates:
            return []
        
        high_quality_count = sum(1 for c in candidates if self._calculate_quality_score(c) >= 0.7)
        
        if high_quality_count >= 5:
            return candidates[:10]
        elif high_quality_count >= 3:
            return candidates[:15]
        else:
            return candidates[:20]
    
    def _calculate_quality_score(self, candidate: CandidateProfile) -> float:
        """Calculate quality score for a candidate."""
        score = 0.0
        
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
        
        if candidate.name and len(candidate.name.strip()) > 2:
            score += 0.3
        
        if candidate.country and candidate.country.strip():
            score += 0.15
        
        if candidate.linkedin_id and candidate.linkedin_id.strip():
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_average_quality(self, candidates: List[CandidateProfile]) -> float:
        """Calculate average quality score."""
        if not candidates:
            return 0.0
        
        total_quality = sum(self._calculate_quality_score(c) for c in candidates)
        return total_quality / len(candidates)
    
    def _format_results(self, candidates: List[CandidateProfile], format_type: str) -> Any:
        """Format results based on detected format."""
        if format_type == 'json':
            return self._format_json(candidates)
        elif format_type == 'csv':
            return self._format_csv(candidates)
        elif format_type == 'summary':
            return self._format_summary(candidates)
        else:  # table
            return self._format_table(candidates)
    
    def _format_json(self, candidates: List[CandidateProfile]) -> List[Dict[str, Any]]:
        """Format as JSON."""
        return [
            {
                'id': c.id,
                'name': c.name or 'Unknown',
                'email': c.email or '',
                'country': c.country or 'Unknown',
                'linkedin_id': c.linkedin_id or '',
                'summary': c.summary or '',
                'quality_score': self._calculate_quality_score(c)
            }
            for c in candidates
        ]
    
    def _format_csv(self, candidates: List[CandidateProfile]) -> str:
        """Format as CSV string."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Name', 'Email', 'Country', 'LinkedIn ID', 'Summary', 'Quality Score'])
        
        # Write data
        for candidate in candidates:
            writer.writerow([
                candidate.id,
                candidate.name or '',
                candidate.email or '',
                candidate.country or '',
                candidate.linkedin_id or '',
                (candidate.summary or '')[:200],  # Truncate summary
                f"{self._calculate_quality_score(candidate):.2f}"
            ])
        
        return output.getvalue()
    
    def _format_table(self, candidates: List[CandidateProfile]) -> List[Dict[str, str]]:
        """Format as table data."""
        return [
            {
                'ID': c.id,
                'Name': c.name or 'N/A',
                'Country': c.country or 'N/A',
                'Summary': (c.summary or 'N/A')[:100] + '...' if len(c.summary or '') > 100 else (c.summary or 'N/A'),
                'Quality': f"{self._calculate_quality_score(c):.2f}"
            }
            for c in candidates
        ]
    
    def _format_summary(self, candidates: List[CandidateProfile]) -> Dict[str, Any]:
        """Format as summary with insights."""
        if not candidates:
            return {'message': 'No candidates found', 'count': 0}
        
        # Calculate summary statistics
        countries = [c.country for c in candidates if c.country]
        quality_scores = [self._calculate_quality_score(c) for c in candidates]
        
        summary = {
            'total_candidates': len(candidates),
            'top_countries': list(set(countries))[:5],
            'average_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'high_quality_count': sum(1 for score in quality_scores if score >= 0.7),
            'top_candidates': [
                {
                    'name': c.name or 'Unknown',
                    'country': c.country or 'Unknown',
                    'quality': self._calculate_quality_score(c)
                }
                for c in candidates[:3]
            ]
        }
        
        return summary

def print_results(result: Dict[str, Any]):
    """Print results in a nice format."""
    print(f"\n{Colors.BOLD}📋 Results ({result['format'].upper()} format):{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
    
    if result['format'] == 'json':
        print(json.dumps(result['formatted_results'], indent=2))
    
    elif result['format'] == 'csv':
        print(result['formatted_results'])
    
    elif result['format'] == 'summary':
        summary = result['formatted_results']
        print(f"📊 Total Candidates: {summary['total_candidates']}")
        print(f"🌍 Top Countries: {', '.join(summary['top_countries'])}")
        print(f"⭐ Average Quality: {summary['average_quality']:.2f}")
        print(f"🏆 High Quality: {summary['high_quality_count']}")
        print(f"\n👥 Top Candidates:")
        for i, candidate in enumerate(summary['top_candidates'], 1):
            print(f"  {i}. {candidate['name']} ({candidate['country']}) - Quality: {candidate['quality']:.2f}")
    
    else:  # table
        table_data = result['formatted_results']
        if table_data:
            # Print header
            print(f"{'ID':<12} | {'Name':<20} | {'Country':<15} | {'Summary':<30}")
            print(f"{Colors.CYAN}{'=' * 80}{Colors.END}")
            
            # Print rows
            for i, candidate in enumerate(table_data[:10], 1):  # Show first 10
                print(f"{candidate['ID']:<12} | {candidate['Name']:<20} | {candidate['Country']:<15} | {candidate['Summary']:<30}")
                
                # Alternate colors
                if i % 2 == 0:
                    print(f"{Colors.GREEN}{'─' * 80}{Colors.END}")
                else:
                    print(f"{Colors.BLUE}{'─' * 80}{Colors.END}")
        
        if len(table_data) > 10:
            print(f"\n{Colors.YELLOW}Showing 10 of {len(table_data)} candidates{Colors.END}")
    
    # Print metadata
    print(f"\n{Colors.BOLD}📈 Performance:{Colors.END}")
    print(f"⏱️  Search Time: {result['search_time']:.2f}s")
    print(f"🎯 Quality Score: {result['quality_score']:.2f}")
    print(f"🤖 GPT Enhanced: {'Yes' if result['gpt_enhanced'] else 'No'}")

async def run_continuous_improvement():
    """Run continuous improvement in background."""
    try:
        # Import and run the continuous evaluation
        from continuous_evaluation import ContinuousEvaluator
        
        evaluator = ContinuousEvaluator()
        logger.info("🚀 Starting continuous improvement in background...")
        
        # Run for a shorter duration in background (1 hour instead of 6)
        await evaluator.run_continuous_evaluation(duration_hours=1)
        
    except Exception as e:
        logger.error(f"Continuous improvement failed: {e}")

def main():
    """Main function."""
    print(f"{Colors.BOLD}{Colors.HEADER}🚀 Smart Search Interface{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
    print("This system automatically detects the best format for your results!")
    print("Just enter your query and get intelligent results.")
    print()
    
    smart_search = SmartSearch()
    
    # Start continuous improvement in background
    improvement_task = None
    try:
        improvement_task = asyncio.create_task(run_continuous_improvement())
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Continuous improvement not available: {e}{Colors.END}")
    
    try:
        while True:
            # Get query from user
            query = input(f"\n{Colors.BLUE}Enter your search query (or 'quit' to exit): {Colors.END}")
            
            if query.lower() in ['quit', 'exit', 'q']:
                print(f"{Colors.YELLOW}Goodbye!{Colors.END}")
                break
            
            if not query.strip():
                print(f"{Colors.YELLOW}Please enter a valid query.{Colors.END}")
                continue
            
            # Perform search
            result = smart_search.search(query.strip())
            
            # Display results
            if result['candidate_count'] > 0:
                print_results(result)
            else:
                print(f"{Colors.YELLOW}No candidates found.{Colors.END}")
            
            print(f"\n{Colors.CYAN}{'=' * 50}{Colors.END}")
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Goodbye!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
    finally:
        # Cancel background task
        if improvement_task:
            improvement_task.cancel()
            try:
                asyncio.get_event_loop().run_until_complete(improvement_task)
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    # Run the main function
    if sys.platform == 'win32':
        # Windows compatibility
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    main() 