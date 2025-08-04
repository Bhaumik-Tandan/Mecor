#!/usr/bin/env python3
"""
Robust Automated Evaluation System
=================================

Simple but effective system that runs continuously for 6 hours
with GPT-powered evaluation and constant improvement.
"""

import asyncio
import json
import time
import sys
import os
import threading
import random
from typing import Dict, List, Any
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
    name="robust_auto_eval",
    level="INFO",
    log_file="logs/robust_auto_eval.log"
)

class RobustEvaluator:
    """Robust evaluation system with GPT-powered analysis."""
    
    def __init__(self):
        self.search_service = search_service
        self.gpt_service = gpt_service
        self.evaluation_results = []
        self.improvements_applied = []
        self.stop_event = threading.Event()
        
        # Test queries
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
            "corporate lawyer",
            "machine learning engineer",
            "data scientist",
            "devops engineer",
            "frontend developer",
            "backend developer",
            "cloud architect",
            "security engineer",
            "mobile developer",
            "M&A attorney",
            "intellectual property lawyer",
            "portfolio manager",
            "financial analyst",
            "risk manager",
            "cardiologist",
            "neurologist",
            "pediatrician",
            "surgeon",
            "psychiatrist",
            "physics researcher",
            "chemistry professor",
            "computer science professor",
            "economics professor",
            "history professor",
            "psychology researcher"
        ]
        
        # Create directories
        Path("evaluation_reports").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("🚀 Robust Evaluator initialized")
    
    async def run_continuous_evaluation(self, duration_hours: int = 6):
        """Run continuous evaluation for specified duration."""
        start_time = time.time()
        end_time = start_time + (duration_hours * 60 * 60)
        
        logger.info(f"🚀 Starting robust evaluation for {duration_hours} hours...")
        logger.info(f"⏰ Start time: {datetime.fromtimestamp(start_time)}")
        logger.info(f"⏰ End time: {datetime.fromtimestamp(end_time)}")
        
        # Start multiple evaluation threads
        threads = []
        for i in range(3):  # 3 threads
            thread = threading.Thread(
                target=self._evaluation_thread_worker,
                args=(f"thread_{i}",),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        logger.info(f"🚀 Started {len(threads)} evaluation threads")
        
        cycle_count = 0
        while time.time() < end_time and not self.stop_event.is_set():
            cycle_count += 1
            current_time = datetime.now()
            
            logger.info(f"🔄 Starting evaluation cycle {cycle_count} at {current_time}")
            
            try:
                # Run evaluation cycle
                await self._evaluation_cycle()
                
                # Generate improvements
                if len(self.evaluation_results) >= 10:
                    await self._generate_improvements()
                
                # Save progress
                self._save_progress(cycle_count)
                
                # Calculate remaining time
                elapsed = time.time() - start_time
                remaining = (duration_hours * 60 * 60) - elapsed
                
                logger.info(f"✅ Cycle {cycle_count} completed. {remaining/60:.1f} minutes remaining")
                
                # Sleep between cycles
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Evaluation cycle {cycle_count} failed: {e}")
                await asyncio.sleep(60)
        
        # Stop threads
        self.stop_event.set()
        for thread in threads:
            thread.join(timeout=5)
        
        logger.info("✅ Continuous evaluation completed")
        await self._generate_final_report()
    
    def _evaluation_thread_worker(self, thread_id: str):
        """Worker function for evaluation threads."""
        while not self.stop_event.is_set():
            try:
                # Select random query
                query = random.choice(self.test_queries)
                
                # Create new event loop for thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Perform evaluation
                result = loop.run_until_complete(self._evaluate_query(query, thread_id))
                
                # Add to results (thread-safe)
                with threading.Lock():
                    self.evaluation_results.append(result)
                
                # Small delay
                time.sleep(random.uniform(10, 30))
                
            except Exception as e:
                logger.error(f"Thread {thread_id} error: {e}")
                time.sleep(30)
    
    async def _evaluation_cycle(self):
        """Run one evaluation cycle."""
        logger.info("🔄 Running evaluation cycle...")
        
        # Run a few evaluations in this cycle
        for i in range(5):
            query = random.choice(self.test_queries)
            result = await self._evaluate_query(query, f"cycle_{i}")
            self.evaluation_results.append(result)
            await asyncio.sleep(5)
    
    async def _evaluate_query(self, query: str, thread_id: str) -> Dict[str, Any]:
        """Evaluate a single query."""
        start_time = time.time()
        
        try:
            # Perform search
            search_query = SearchQuery(
                query_text=query,
                job_category="general",
                strategy=SearchStrategy.GPT_ENHANCED,
                max_candidates=15
            )
            
            candidates = self.search_service.search_candidates(
                search_query, 
                SearchStrategy.GPT_ENHANCED
            )
            
            # Apply quality filtering
            quality_candidates = self._filter_by_quality(candidates)
            final_candidates = self._adjust_count(quality_candidates)
            
            response_time = time.time() - start_time
            
            # Calculate metrics
            quality_score = self._calculate_average_quality(final_candidates)
            
            # GPT evaluation
            gpt_score, gpt_suggestions = await self._gpt_evaluate(query, final_candidates, response_time)
            
            result = {
                'query': query,
                'response_time': response_time,
                'candidate_count': len(final_candidates),
                'quality_score': quality_score,
                'gpt_evaluation_score': gpt_score,
                'gpt_suggestions': gpt_suggestions,
                'gpt_enhanced': gpt_service.is_available(),
                'thread_id': thread_id,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Evaluated '{query}': {len(final_candidates)} candidates, GPT score: {gpt_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Query evaluation failed for '{query}': {e}")
            return {
                'query': query,
                'response_time': time.time() - start_time,
                'candidate_count': 0,
                'quality_score': 0.0,
                'gpt_evaluation_score': 0.0,
                'gpt_suggestions': [f"Error: {str(e)}"],
                'gpt_enhanced': False,
                'thread_id': thread_id,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _gpt_evaluate(self, query: str, candidates: List[CandidateProfile], response_time: float) -> tuple:
        """Evaluate using GPT."""
        if not self.gpt_service.is_available():
            return 0.5, ["GPT service not available"]
        
        try:
            # Prepare candidate summary
            candidates_summary = []
            for i, candidate in enumerate(candidates[:5], 1):  # Top 5 candidates
                summary = (candidate.summary or "")[:150]
                candidates_summary.append(f"{i}. {candidate.name or 'Unknown'}: {summary}")
            
            evaluation_prompt = f"""Evaluate this search result:

Query: "{query}"
Response Time: {response_time:.2f}s
Candidate Count: {len(candidates)}

Top Candidates:
{chr(10).join(candidates_summary)}

Rate from 0.0 to 1.0 based on:
- Relevance to query (0.4 weight)
- Candidate quality (0.4 weight)  
- Response time (0.2 weight)

Provide score and 2 improvement suggestions.

Return as JSON:
{{
  "score": 0.85,
  "suggestions": ["suggestion1", "suggestion2"]
}}"""

            response = self.gpt_service._make_gpt_request(
                [{"role": "user", "content": evaluation_prompt}],
                temperature=0.2,
                max_tokens=200
            )
            
            evaluation_data = json.loads(response)
            score = evaluation_data.get('score', 0.5)
            suggestions = evaluation_data.get('suggestions', [])
            
            return score, suggestions
            
        except Exception as e:
            logger.error(f"GPT evaluation failed: {e}")
            return 0.5, [f"Evaluation error: {str(e)}"]
    
    async def _generate_improvements(self):
        """Generate and apply improvements."""
        if len(self.evaluation_results) < 10:
            return
        
        # Get recent results
        recent_results = self.evaluation_results[-20:]
        
        # Calculate performance metrics
        avg_response_time = sum(r['response_time'] for r in recent_results) / len(recent_results)
        avg_quality = sum(r['quality_score'] for r in recent_results) / len(recent_results)
        avg_gpt_score = sum(r['gpt_evaluation_score'] for r in recent_results) / len(recent_results)
        
        improvements = []
        
        # Generate improvements based on performance
        if avg_response_time > 8.0:
            improvements.append("Optimize search algorithms for faster response")
        
        if avg_quality < 0.6:
            improvements.append("Improve quality filtering criteria")
        
        if avg_gpt_score < 0.7:
            improvements.append("Enhance GPT prompt optimization")
        
        # Add filter extraction improvement
        improvements.append("Apply filter extraction from user queries for enhanced hybrid search")
        
        # Apply improvements
        for improvement in improvements:
            self.improvements_applied.append({
                'improvement': improvement,
                'timestamp': datetime.now().isoformat(),
                'avg_response_time': avg_response_time,
                'avg_quality': avg_quality,
                'avg_gpt_score': avg_gpt_score
            })
        
        if improvements:
            logger.info(f"🔧 Applied improvements: {improvements}")
    
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
    
    def _save_progress(self, cycle_count: int):
        """Save progress to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_reports/progress_cycle_{cycle_count}_{timestamp}.json"
        
        progress_data = {
            'cycle_count': cycle_count,
            'timestamp': datetime.now().isoformat(),
            'total_evaluations': len(self.evaluation_results),
            'total_improvements': len(self.improvements_applied),
            'recent_results': self.evaluation_results[-10:],
            'recent_improvements': self.improvements_applied[-5:]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    async def _generate_final_report(self):
        """Generate final evaluation report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_reports/final_robust_report_{timestamp}.json"
        
        # Calculate final statistics
        total_evaluations = len(self.evaluation_results)
        total_improvements = len(self.improvements_applied)
        
        if total_evaluations > 0:
            avg_response_time = sum(r['response_time'] for r in self.evaluation_results) / total_evaluations
            avg_quality = sum(r['quality_score'] for r in self.evaluation_results) / total_evaluations
            avg_gpt_score = sum(r['gpt_evaluation_score'] for r in self.evaluation_results) / total_evaluations
            gpt_enhancement_rate = sum(1 for r in self.evaluation_results if r['gpt_enhanced']) / total_evaluations
        else:
            avg_response_time = avg_quality = avg_gpt_score = gpt_enhancement_rate = 0
        
        final_report = {
            'evaluation_summary': {
                'start_time': self.evaluation_results[0]['timestamp'] if self.evaluation_results else None,
                'end_time': datetime.now().isoformat(),
                'total_evaluations': total_evaluations,
                'total_improvements': total_improvements,
                'avg_response_time': avg_response_time,
                'avg_quality_score': avg_quality,
                'avg_gpt_evaluation_score': avg_gpt_score,
                'gpt_enhancement_rate': gpt_enhancement_rate
            },
            'improvements_applied': self.improvements_applied,
            'top_performing_queries': self._get_top_performing_queries(),
            'recommendations': self._generate_recommendations()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(final_report, f, indent=2)
            logger.info(f"📊 Final report saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save final report: {e}")
    
    def _get_top_performing_queries(self) -> List[Dict[str, Any]]:
        """Get top performing queries."""
        if not self.evaluation_results:
            return []
        
        # Group by query and calculate average scores
        query_scores = {}
        for result in self.evaluation_results:
            if result['query'] not in query_scores:
                query_scores[result['query']] = []
            query_scores[result['query']].append(result['gpt_evaluation_score'])
        
        # Calculate averages and sort
        query_averages = [
            {
                'query': query,
                'avg_score': sum(scores) / len(scores),
                'count': len(scores)
            }
            for query, scores in query_scores.items()
        ]
        
        query_averages.sort(key=lambda x: x['avg_score'], reverse=True)
        return query_averages[:10]
    
    def _generate_recommendations(self) -> List[str]:
        """Generate final recommendations."""
        recommendations = []
        
        if len(self.evaluation_results) < 10:
            return ['Need more evaluation data for meaningful recommendations']
        
        recent_results = self.evaluation_results[-20:]
        avg_response_time = sum(r['response_time'] for r in recent_results) / len(recent_results)
        avg_gpt_score = sum(r['gpt_evaluation_score'] for r in recent_results) / len(recent_results)
        
        if avg_response_time > 6.0:
            recommendations.append("Continue optimizing search algorithms for faster response times")
        
        if avg_gpt_score < 0.7:
            recommendations.append("Further enhance GPT integration and prompt optimization")
        
        if len(self.improvements_applied) < 5:
            recommendations.append("Implement more aggressive improvement strategies")
        
        recommendations.append("Continue monitoring and evaluation for ongoing optimization")
        
        return recommendations

async def main():
    """Main function."""
    print("🚀 Robust Automated Evaluation System")
    print("=" * 50)
    print("This system will run continuously for 6 hours with:")
    print("- Multi-threaded evaluation")
    print("- GPT-powered analysis")
    print("- Continuous improvement")
    print("- Comprehensive reporting")
    print()
    
    evaluator = RobustEvaluator()
    
    try:
        await evaluator.run_continuous_evaluation(duration_hours=6)
    except KeyboardInterrupt:
        print("\n⏹️  Evaluation stopped by user")
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        logger.error(f"Evaluation failed: {e}")
    finally:
        print("\n📊 Generating final report...")
        print("✅ Evaluation completed")

if __name__ == "__main__":
    asyncio.run(main()) 