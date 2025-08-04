#!/usr/bin/env python3
"""
Mercor MCP Server - Comprehensive Search and Evaluation System
==============================================================

This server provides:
1. Intelligent format detection using GPT
2. Multiple output formats (JSON, CSV, Table, Summary)
3. Continuous evaluation and improvement
4. Real-time system monitoring
"""

import asyncio
import json
import time
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import csv
import io
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
    name="mcp_server",
    level="INFO",
    log_file="logs/mcp_server.log"
)

@dataclass
class SearchRequest:
    """Search request with format preferences."""
    query: str
    format: Optional[str] = None  # json, csv, table, summary, auto
    max_candidates: int = 20
    include_metadata: bool = True
    category: Optional[str] = None

@dataclass
class SearchResult:
    """Structured search result."""
    candidates: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    format: str
    query: str
    timestamp: str
    search_time: float
    quality_score: float

@dataclass
class EvaluationResult:
    """Evaluation result for continuous improvement."""
    query: str
    expected_format: str
    actual_format: str
    format_match: bool
    quality_score: float
    response_time: float
    candidate_count: int
    gpt_enhanced: bool
    suggestions: List[str]
    timestamp: str

class FormatDetector:
    """Intelligent format detection using GPT."""
    
    def __init__(self):
        self.gpt_service = gpt_service
        self.format_patterns = {
            'json': ['json', 'object', 'data', 'api', 'programmatic'],
            'csv': ['csv', 'excel', 'spreadsheet', 'table', 'data analysis'],
            'table': ['table', 'list', 'display', 'view', 'show'],
            'summary': ['summary', 'overview', 'brief', 'summary', 'report']
        }
    
    def detect_format(self, query: str, user_format: Optional[str] = None) -> str:
        """Detect the best format for the query."""
        if user_format and user_format.lower() in ['json', 'csv', 'table', 'summary']:
            return user_format.lower()
        
        if not self.gpt_service.is_available():
            return self._fallback_detection(query)
        
        try:
            prompt = f"""Analyze this search query and determine the best output format:

Query: "{query}"

Available formats:
- json: For API integration, data processing, programmatic use
- csv: For spreadsheet analysis, data export, bulk processing
- table: For human-readable display, quick overview, presentation
- summary: For brief overview, executive summary, high-level insights

Consider:
1. User intent and context
2. Likely use case
3. Technical vs non-technical audience
4. Data processing needs

Return ONLY the format name: json, csv, table, or summary"""

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
        
        return self._fallback_detection(query)
    
    def _fallback_detection(self, query: str) -> str:
        """Fallback format detection using keyword matching."""
        query_lower = query.lower()
        
        for format_name, keywords in self.format_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return format_name
        
        return 'table'  # Default to table format

class ResultFormatter:
    """Format search results into different output formats."""
    
    def __init__(self):
        self.format_detector = FormatDetector()
    
    def format_results(self, candidates: List[CandidateProfile], request: SearchRequest, metadata: Dict[str, Any]) -> SearchResult:
        """Format results based on detected or specified format."""
        format_type = self.format_detector.detect_format(request.query, request.format)
        
        if format_type == 'json':
            formatted_data = self._format_json(candidates, metadata)
        elif format_type == 'csv':
            formatted_data = self._format_csv(candidates, metadata)
        elif format_type == 'summary':
            formatted_data = self._format_summary(candidates, metadata)
        else:  # table
            formatted_data = self._format_table(candidates, metadata)
        
        return SearchResult(
            candidates=formatted_data,
            metadata=metadata,
            format=format_type,
            query=request.query,
            timestamp=datetime.now().isoformat(),
            search_time=metadata.get('search_time', 0),
            quality_score=metadata.get('quality_score', 0)
        )
    
    def _format_json(self, candidates: List[CandidateProfile], metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format as JSON-compatible data."""
        return [
            {
                'id': c.id,
                'name': c.name,
                'email': c.email,
                'summary': c.summary,
                'linkedin_id': c.linkedin_id,
                'country': c.country,
                'quality_score': self._calculate_quality_score(c)
            }
            for c in candidates
        ]
    
    def _format_csv(self, candidates: List[CandidateProfile], metadata: Dict[str, Any]) -> str:
        """Format as CSV string."""
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
    
    def _format_table(self, candidates: List[CandidateProfile], metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format as table data."""
        return [
            {
                'ID': c.id,
                'Name': c.name or 'N/A',
                'Country': c.country or 'N/A',
                'Summary': (candidate.summary or 'N/A')[:100] + '...' if len(candidate.summary or '') > 100 else (candidate.summary or 'N/A'),
                'Quality': f"{self._calculate_quality_score(c):.2f}"
            }
            for c in candidates
        ]
    
    def _format_summary(self, candidates: List[CandidateProfile], metadata: Dict[str, Any]) -> Dict[str, Any]:
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
            'search_time': metadata.get('search_time', 0),
            'gpt_enhanced': metadata.get('gpt_enhanced', False),
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

class EvaluationEngine:
    """Continuous evaluation and improvement engine."""
    
    def __init__(self):
        self.gpt_service = gpt_service
        self.evaluation_results = []
        self.improvement_suggestions = []
        self.test_queries = [
            "experienced software engineer",
            "tax lawyer",
            "quantitative finance expert",
            "biology researcher",
            "investment banker",
            "mathematics professor",
            "radiology doctor",
            "mechanical engineer",
            "anthropology PhD",
            "corporate lawyer"
        ]
    
    async def run_continuous_evaluation(self, search_engine, formatter):
        """Run continuous evaluation for 6 hours."""
        start_time = time.time()
        end_time = start_time + (6 * 60 * 60)  # 6 hours
        
        logger.info("🚀 Starting continuous evaluation for 6 hours...")
        
        while time.time() < end_time:
            try:
                # Run evaluation cycle
                await self._evaluation_cycle(search_engine, formatter)
                
                # Generate improvement suggestions
                suggestions = self._generate_improvement_suggestions()
                if suggestions:
                    logger.info(f"💡 Improvement suggestions: {suggestions}")
                
                # Wait before next cycle
                await asyncio.sleep(300)  # 5 minutes between cycles
                
            except Exception as e:
                logger.error(f"Evaluation cycle failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
        
        logger.info("✅ Continuous evaluation completed")
        self._save_evaluation_report()
    
    async def _evaluation_cycle(self, search_engine, formatter):
        """Run one evaluation cycle."""
        logger.info("🔄 Running evaluation cycle...")
        
        for query in self.test_queries:
            try:
                # Test different formats
                for format_type in ['auto', 'json', 'csv', 'table', 'summary']:
                    request = SearchRequest(
                        query=query,
                        format=format_type,
                        max_candidates=15
                    )
                    
                    # Perform search
                    start_time = time.time()
                    candidates, metadata = await search_engine.search(request)
                    search_time = time.time() - start_time
                    
                    # Format results
                    result = formatter.format_results(candidates, request, metadata)
                    
                    # Evaluate result
                    evaluation = self._evaluate_result(request, result, search_time)
                    self.evaluation_results.append(evaluation)
                    
                    # Small delay between tests
                    await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Query evaluation failed for '{query}': {e}")
    
    def _evaluate_result(self, request: SearchRequest, result: SearchResult, search_time: float) -> EvaluationResult:
        """Evaluate a search result."""
        format_match = request.format == 'auto' or request.format == result.format
        
        # Calculate quality metrics
        quality_score = result.quality_score
        candidate_count = len(result.candidates)
        
        # Generate suggestions using GPT
        suggestions = self._generate_suggestions(request, result, search_time)
        
        return EvaluationResult(
            query=request.query,
            expected_format=request.format or 'auto',
            actual_format=result.format,
            format_match=format_match,
            quality_score=quality_score,
            response_time=search_time,
            candidate_count=candidate_count,
            gpt_enhanced=result.metadata.get('gpt_enhanced', False),
            suggestions=suggestions,
            timestamp=datetime.now().isoformat()
        )
    
    def _generate_suggestions(self, request: SearchRequest, result: SearchResult, search_time: float) -> List[str]:
        """Generate improvement suggestions using GPT."""
        if not self.gpt_service.is_available():
            return []
        
        try:
            prompt = f"""Analyze this search result and provide improvement suggestions:

Query: "{request.query}"
Format: {result.format}
Response Time: {search_time:.2f}s
Candidate Count: {len(result.candidates)}
Quality Score: {result.quality_score:.2f}
GPT Enhanced: {result.metadata.get('gpt_enhanced', False)}

Provide 2-3 specific, actionable suggestions to improve:
1. Search quality
2. Response time
3. Format detection
4. User experience

Return suggestions as a JSON array: ["suggestion1", "suggestion2", "suggestion3"]"""

            response = self.gpt_service._make_gpt_request(
                [{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            suggestions = json.loads(response)
            if isinstance(suggestions, list):
                return suggestions
            
        except Exception as e:
            logger.warning(f"Failed to generate suggestions: {e}")
        
        return []
    
    def _generate_improvement_suggestions(self) -> List[str]:
        """Generate overall improvement suggestions based on evaluation history."""
        if not self.evaluation_results:
            return []
        
        # Analyze recent results
        recent_results = self.evaluation_results[-50:]  # Last 50 results
        
        avg_quality = sum(r.quality_score for r in recent_results) / len(recent_results)
        avg_response_time = sum(r.response_time for r in recent_results) / len(recent_results)
        format_accuracy = sum(1 for r in recent_results if r.format_match) / len(recent_results)
        
        suggestions = []
        
        if avg_quality < 0.6:
            suggestions.append("Improve candidate quality filtering")
        
        if avg_response_time > 10:
            suggestions.append("Optimize search performance")
        
        if format_accuracy < 0.8:
            suggestions.append("Enhance format detection accuracy")
        
        return suggestions
    
    def _save_evaluation_report(self):
        """Save evaluation report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_evaluations': len(self.evaluation_results),
            'summary': {
                'avg_quality_score': sum(r.quality_score for r in self.evaluation_results) / len(self.evaluation_results),
                'avg_response_time': sum(r.response_time for r in self.evaluation_results) / len(self.evaluation_results),
                'format_accuracy': sum(1 for r in self.evaluation_results if r.format_match) / len(self.evaluation_results),
                'gpt_enhancement_rate': sum(1 for r in self.evaluation_results if r.gpt_enhanced) / len(self.evaluation_results)
            },
            'results': [asdict(r) for r in self.evaluation_results]
        }
        
        try:
            with open(f"evaluation_reports/{filename}", 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📊 Evaluation report saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save evaluation report: {e}")

class MercorMCPServer:
    """Main MCP server class."""
    
    def __init__(self):
        self.search_service = search_service
        self.formatter = ResultFormatter()
        self.evaluation_engine = EvaluationEngine()
        self.is_evaluating = False
        
        # Create directories
        Path("evaluation_reports").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("🚀 Mercor MCP Server initialized")
    
    async def search(self, request: SearchRequest) -> SearchResult:
        """Perform search with format detection."""
        start_time = time.time()
        
        logger.info(f"🔍 Processing search: {request.query} (format: {request.format or 'auto'})")
        
        try:
            # Perform search
            candidates = await self._perform_search(request)
            
            # Calculate metadata
            search_time = time.time() - start_time
            metadata = {
                'search_time': search_time,
                'candidate_count': len(candidates),
                'gpt_enhanced': gpt_service.is_available(),
                'quality_score': sum(self.formatter._calculate_quality_score(c) for c in candidates) / len(candidates) if candidates else 0
            }
            
            # Format results
            result = self.formatter.format_results(candidates, request, metadata)
            
            logger.info(f"✅ Search completed: {len(candidates)} candidates in {search_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise
    
    async def _perform_search(self, request: SearchRequest) -> List[CandidateProfile]:
        """Perform the actual search."""
        search_query = SearchQuery(
            query_text=request.query,
            job_category=request.category or "general",
            strategy=SearchStrategy.GPT_ENHANCED,
            max_candidates=request.max_candidates
        )
        
        candidates = self.search_service.search_candidates(
            search_query, 
            SearchStrategy.GPT_ENHANCED
        )
        
        # Apply quality filtering
        quality_candidates = self._filter_by_quality(candidates)
        
        # Adjust count based on quality
        final_candidates = self._adjust_count(quality_candidates)
        
        return final_candidates
    
    def _filter_by_quality(self, candidates: List[CandidateProfile]) -> List[CandidateProfile]:
        """Filter candidates by quality."""
        if not candidates:
            return []
        
        quality_candidates = []
        for candidate in candidates:
            quality_score = self.formatter._calculate_quality_score(candidate)
            if quality_score >= 0.4:
                quality_candidates.append(candidate)
        
        quality_candidates.sort(key=lambda c: self.formatter._calculate_quality_score(c), reverse=True)
        return quality_candidates
    
    def _adjust_count(self, candidates: List[CandidateProfile]) -> List[CandidateProfile]:
        """Adjust candidate count based on quality."""
        if not candidates:
            return []
        
        high_quality_count = sum(1 for c in candidates if self.formatter._calculate_quality_score(c) >= 0.7)
        
        if high_quality_count >= 5:
            return candidates[:10]
        elif high_quality_count >= 3:
            return candidates[:15]
        else:
            return candidates[:20]
    
    async def start_evaluation(self):
        """Start continuous evaluation."""
        if self.is_evaluating:
            logger.warning("Evaluation already running")
            return
        
        self.is_evaluating = True
        logger.info("🚀 Starting continuous evaluation...")
        
        try:
            await self.evaluation_engine.run_continuous_evaluation(self, self.formatter)
        finally:
            self.is_evaluating = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get server status."""
        return {
            'status': 'running',
            'evaluation_active': self.is_evaluating,
            'gpt_available': gpt_service.is_available(),
            'total_evaluations': len(self.evaluation_engine.evaluation_results),
            'timestamp': datetime.now().isoformat()
        }

# Global server instance
server = MercorMCPServer()

async def main():
    """Main function for testing the MCP server."""
    print("🚀 Mercor MCP Server")
    print("=" * 50)
    
    # Start evaluation in background
    evaluation_task = asyncio.create_task(server.start_evaluation())
    
    try:
        # Simple interactive mode for testing
        while True:
            query = input("\nEnter search query (or 'quit' to exit): ")
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query.strip():
                continue
            
            # Ask for format preference
            format_pref = input("Format (json/csv/table/summary/auto): ").strip() or 'auto'
            
            request = SearchRequest(
                query=query.strip(),
                format=format_pref if format_pref != 'auto' else None,
                max_candidates=15
            )
            
            try:
                result = await server.search(request)
                
                print(f"\n✅ Found {len(result.candidates)} candidates")
                print(f"📊 Format: {result.format}")
                print(f"⏱️  Time: {result.search_time:.2f}s")
                print(f"🎯 Quality: {result.quality_score:.2f}")
                
                # Display results based on format
                if result.format == 'json':
                    print(json.dumps(result.candidates, indent=2))
                elif result.format == 'csv':
                    print(result.candidates)  # CSV string
                elif result.format == 'summary':
                    print(json.dumps(result.candidates, indent=2))
                else:  # table
                    for candidate in result.candidates[:5]:  # Show first 5
                        print(f"{candidate['Name']} | {candidate['Country']} | {candidate['Summary']}")
                
            except Exception as e:
                print(f"❌ Search failed: {e}")
    
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        evaluation_task.cancel()
        try:
            await evaluation_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main()) 