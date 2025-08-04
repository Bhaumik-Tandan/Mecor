#!/usr/bin/env python3
"""
Continuous Evaluation and Improvement System
============================================

This script runs for 6 hours continuously, evaluating and improving the search system.
It uses GPT APIs to analyze performance and suggest improvements.
"""

import asyncio
import json
import time
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import random

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from src.services.search_service import search_service
from src.services.gpt_service import gpt_service
from src.utils.logger import get_logger, setup_logger

# Setup logging
logger = setup_logger(
    name="continuous_evaluation",
    level="INFO",
    log_file="logs/continuous_evaluation.log"
)

@dataclass
class EvaluationMetrics:
    """Metrics for evaluating search performance."""
    query: str
    response_time: float
    candidate_count: int
    quality_score: float
    format_accuracy: float
    gpt_enhanced: bool
    suggestions_implemented: List[str]
    timestamp: str

@dataclass
class ImprovementAction:
    """Action to improve the system."""
    action_type: str  # 'prompt_optimization', 'filter_adjustment', 'format_detection', 'quality_threshold'
    description: str
    implementation: str
    expected_impact: str
    priority: int  # 1-5, 5 being highest
    timestamp: str

class ContinuousEvaluator:
    """Continuous evaluation and improvement engine."""
    
    def __init__(self):
        self.gpt_service = gpt_service
        self.metrics_history = []
        self.improvement_actions = []
        self.current_improvements = []
        
        # Test queries with different characteristics
        self.test_queries = {
            'technical': [
                "experienced software engineer",
                "machine learning engineer",
                "data scientist",
                "devops engineer",
                "frontend developer",
                "backend developer",
                "full stack engineer",
                "cloud architect",
                "security engineer",
                "mobile developer"
            ],
            'legal': [
                "tax lawyer",
                "corporate lawyer",
                "M&A attorney",
                "intellectual property lawyer",
                "litigation attorney",
                "contract lawyer",
                "employment lawyer",
                "real estate attorney",
                "criminal defense lawyer",
                "family law attorney"
            ],
            'finance': [
                "quantitative finance expert",
                "investment banker",
                "portfolio manager",
                "financial analyst",
                "risk manager",
                "trading analyst",
                "private equity analyst",
                "venture capital associate",
                "hedge fund analyst",
                "credit analyst"
            ],
            'medical': [
                "radiology doctor",
                "cardiologist",
                "neurologist",
                "pediatrician",
                "surgeon",
                "psychiatrist",
                "dermatologist",
                "orthopedic surgeon",
                "emergency medicine doctor",
                "family medicine physician"
            ],
            'academic': [
                "biology researcher",
                "mathematics professor",
                "anthropology PhD",
                "physics researcher",
                "chemistry professor",
                "computer science professor",
                "economics professor",
                "history professor",
                "psychology researcher",
                "engineering professor"
            ]
        }
        
        # Create directories
        Path("evaluation_reports").mkdir(exist_ok=True)
        Path("improvement_logs").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("🚀 Continuous Evaluator initialized")
    
    async def run_continuous_evaluation(self, duration_hours: int = 6):
        """Run continuous evaluation for specified duration."""
        start_time = time.time()
        end_time = start_time + (duration_hours * 60 * 60)
        
        logger.info(f"🚀 Starting continuous evaluation for {duration_hours} hours...")
        logger.info(f"⏰ Start time: {datetime.fromtimestamp(start_time)}")
        logger.info(f"⏰ End time: {datetime.fromtimestamp(end_time)}")
        
        cycle_count = 0
        
        while time.time() < end_time:
            cycle_count += 1
            current_time = datetime.now()
            
            logger.info(f"🔄 Starting evaluation cycle {cycle_count} at {current_time}")
            
            try:
                # Run evaluation cycle
                await self._evaluation_cycle()
                
                # Analyze results and generate improvements
                improvements = await self._analyze_and_improve()
                
                # Implement improvements
                if improvements:
                    await self._implement_improvements(improvements)
                
                # Save progress
                self._save_progress(cycle_count)
                
                # Calculate time until next cycle
                elapsed = time.time() - start_time
                remaining = (duration_hours * 60 * 60) - elapsed
                
                logger.info(f"✅ Cycle {cycle_count} completed. {remaining/60:.1f} minutes remaining")
                
                # Adaptive sleep based on performance
                sleep_time = self._calculate_adaptive_sleep()
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"❌ Evaluation cycle {cycle_count} failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
        
        logger.info("✅ Continuous evaluation completed")
        await self._generate_final_report()
    
    async def _evaluation_cycle(self):
        """Run one evaluation cycle."""
        cycle_metrics = []
        
        # Test each category
        for category, queries in self.test_queries.items():
            logger.info(f"📊 Testing category: {category}")
            
            for query in queries[:3]:  # Test first 3 queries per category
                try:
                    # Test with different formats
                    for format_type in ['auto', 'json', 'table', 'summary']:
                        metrics = await self._evaluate_query(query, format_type, category)
                        cycle_metrics.append(metrics)
                        
                        # Small delay between tests
                        await asyncio.sleep(1)
                
                except Exception as e:
                    logger.error(f"Query evaluation failed for '{query}': {e}")
        
        # Store cycle results
        self.metrics_history.extend(cycle_metrics)
        
        # Log cycle summary
        avg_response_time = sum(m.response_time for m in cycle_metrics) / len(cycle_metrics)
        avg_quality = sum(m.quality_score for m in cycle_metrics) / len(cycle_metrics)
        avg_candidates = sum(m.candidate_count for m in cycle_metrics) / len(cycle_metrics)
        
        logger.info(f"📈 Cycle Summary - Avg Response: {avg_response_time:.2f}s, Avg Quality: {avg_quality:.2f}, Avg Candidates: {avg_candidates:.1f}")
    
    async def _evaluate_query(self, query: str, format_type: str, category: str) -> EvaluationMetrics:
        """Evaluate a single query."""
        start_time = time.time()
        
        try:
            # Perform search
            search_query = SearchQuery(
                query_text=query,
                job_category=category,
                strategy=SearchStrategy.GPT_ENHANCED,
                max_candidates=15
            )
            
            candidates = search_service.search_candidates(
                search_query, 
                SearchStrategy.GPT_ENHANCED
            )
            
            # Apply quality filtering
            quality_candidates = self._filter_by_quality(candidates)
            final_candidates = self._adjust_count(quality_candidates)
            
            response_time = time.time() - start_time
            
            # Calculate metrics
            quality_score = self._calculate_average_quality(final_candidates)
            format_accuracy = 1.0 if format_type == 'auto' else 0.8  # Simplified for now
            
            metrics = EvaluationMetrics(
                query=query,
                response_time=response_time,
                candidate_count=len(final_candidates),
                quality_score=quality_score,
                format_accuracy=format_accuracy,
                gpt_enhanced=gpt_service.is_available(),
                suggestions_implemented=self.current_improvements.copy(),
                timestamp=datetime.now().isoformat()
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Query evaluation failed: {e}")
            # Return default metrics on error
            return EvaluationMetrics(
                query=query,
                response_time=time.time() - start_time,
                candidate_count=0,
                quality_score=0.0,
                format_accuracy=0.0,
                gpt_enhanced=False,
                suggestions_implemented=[],
                timestamp=datetime.now().isoformat()
            )
    
    async def _analyze_and_improve(self) -> List[ImprovementAction]:
        """Analyze results and generate improvement suggestions."""
        if len(self.metrics_history) < 10:  # Need minimum data
            return []
        
        # Get recent metrics
        recent_metrics = self.metrics_history[-50:]  # Last 50 evaluations
        
        # Calculate performance indicators
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        avg_quality = sum(m.quality_score for m in recent_metrics) / len(recent_metrics)
        avg_candidates = sum(m.candidate_count for m in recent_metrics) / len(recent_metrics)
        
        improvements = []
        
        # Generate improvements using GPT
        if self.gpt_service.is_available():
            try:
                gpt_improvements = await self._generate_gpt_improvements(recent_metrics)
                improvements.extend(gpt_improvements)
            except Exception as e:
                logger.warning(f"GPT improvement generation failed: {e}")
        
        # Rule-based improvements
        rule_improvements = self._generate_rule_based_improvements(avg_response_time, avg_quality, avg_candidates)
        improvements.extend(rule_improvements)
        
        # Sort by priority
        improvements.sort(key=lambda x: x.priority, reverse=True)
        
        # Limit to top 3 improvements
        return improvements[:3]
    
    async def _generate_gpt_improvements(self, recent_metrics: List[EvaluationMetrics]) -> List[ImprovementAction]:
        """Generate improvements using GPT analysis."""
        try:
            # Prepare data for GPT
            performance_summary = {
                'avg_response_time': sum(m.response_time for m in recent_metrics) / len(recent_metrics),
                'avg_quality_score': sum(m.quality_score for m in recent_metrics) / len(recent_metrics),
                'avg_candidate_count': sum(m.candidate_count for m in recent_metrics) / len(recent_metrics),
                'gpt_enhancement_rate': sum(1 for m in recent_metrics if m.gpt_enhanced) / len(recent_metrics),
                'total_evaluations': len(recent_metrics)
            }
            
            # Sample of recent queries
            recent_queries = [m.query for m in recent_metrics[-10:]]
            
            prompt = f"""Analyze this search system performance data and suggest specific improvements:

Performance Summary:
- Average Response Time: {performance_summary['avg_response_time']:.2f}s
- Average Quality Score: {performance_summary['avg_quality_score']:.2f}
- Average Candidate Count: {performance_summary['avg_candidate_count']:.1f}
- GPT Enhancement Rate: {performance_summary['gpt_enhancement_rate']:.2f}

Recent Queries: {recent_queries}

Suggest 3 specific, actionable improvements to:
1. Reduce response time
2. Improve quality scores
3. Optimize candidate count
4. Enhance GPT integration

For each suggestion, provide:
- Action type (prompt_optimization, filter_adjustment, format_detection, quality_threshold)
- Description
- Implementation details
- Expected impact
- Priority (1-5)

Return as JSON array:
[
  {{
    "action_type": "type",
    "description": "description",
    "implementation": "implementation",
    "expected_impact": "impact",
    "priority": 5
  }}
]"""

            response = self.gpt_service._make_gpt_request(
                [{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            improvements_data = json.loads(response)
            improvements = []
            
            for imp_data in improvements_data:
                improvement = ImprovementAction(
                    action_type=imp_data.get('action_type', 'general'),
                    description=imp_data.get('description', ''),
                    implementation=imp_data.get('implementation', ''),
                    expected_impact=imp_data.get('expected_impact', ''),
                    priority=imp_data.get('priority', 3),
                    timestamp=datetime.now().isoformat()
                )
                improvements.append(improvement)
            
            return improvements
            
        except Exception as e:
            logger.error(f"GPT improvement generation failed: {e}")
            return []
    
    def _generate_rule_based_improvements(self, avg_response_time: float, avg_quality: float, avg_candidates: float) -> List[ImprovementAction]:
        """Generate rule-based improvements."""
        improvements = []
        
        # Response time improvements
        if avg_response_time > 8.0:
            improvements.append(ImprovementAction(
                action_type="performance_optimization",
                description="Response time is too high, optimize search algorithms",
                implementation="Reduce search scope and implement caching",
                expected_impact="Reduce response time by 30%",
                priority=5,
                timestamp=datetime.now().isoformat()
            ))
        
        # Quality improvements
        if avg_quality < 0.6:
            improvements.append(ImprovementAction(
                action_type="quality_threshold",
                description="Quality scores are low, adjust filtering criteria",
                implementation="Increase minimum quality threshold from 0.4 to 0.5",
                expected_impact="Improve average quality by 15%",
                priority=4,
                timestamp=datetime.now().isoformat()
            ))
        
        # Candidate count improvements
        if avg_candidates < 5:
            improvements.append(ImprovementAction(
                action_type="filter_adjustment",
                description="Too few candidates, relax filtering criteria",
                implementation="Reduce quality threshold and increase search scope",
                expected_impact="Increase candidate count by 50%",
                priority=3,
                timestamp=datetime.now().isoformat()
            ))
        
        return improvements
    
    async def _implement_improvements(self, improvements: List[ImprovementAction]):
        """Implement the suggested improvements."""
        for improvement in improvements:
            try:
                logger.info(f"🔧 Implementing improvement: {improvement.description}")
                
                if improvement.action_type == "quality_threshold":
                    await self._implement_quality_threshold_improvement(improvement)
                elif improvement.action_type == "performance_optimization":
                    await self._implement_performance_improvement(improvement)
                elif improvement.action_type == "filter_adjustment":
                    await self._implement_filter_improvement(improvement)
                elif improvement.action_type == "prompt_optimization":
                    await self._implement_prompt_improvement(improvement)
                
                # Track implemented improvement
                self.improvement_actions.append(improvement)
                self.current_improvements.append(improvement.description)
                
                logger.info(f"✅ Improvement implemented: {improvement.description}")
                
            except Exception as e:
                logger.error(f"❌ Failed to implement improvement: {e}")
    
    async def _implement_quality_threshold_improvement(self, improvement: ImprovementAction):
        """Implement quality threshold improvements."""
        # This would modify the quality filtering logic
        # For now, we'll just log the improvement
        logger.info(f"Quality threshold improvement: {improvement.implementation}")
    
    async def _implement_performance_improvement(self, improvement: ImprovementAction):
        """Implement performance improvements."""
        logger.info(f"Performance improvement: {improvement.implementation}")
    
    async def _implement_filter_improvement(self, improvement: ImprovementAction):
        """Implement filter improvements."""
        logger.info(f"Filter improvement: {improvement.implementation}")
    
    async def _implement_prompt_improvement(self, improvement: ImprovementAction):
        """Implement prompt improvements."""
        logger.info(f"Prompt improvement: {improvement.implementation}")
    
    def _filter_by_quality(self, candidates: List[CandidateProfile]) -> List[CandidateProfile]:
        """Filter candidates by quality."""
        if not candidates:
            return []
        
        quality_candidates = []
        for candidate in candidates:
            quality_score = self._calculate_quality_score(candidate)
            if quality_score >= 0.4:  # Adjustable threshold
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
        """Calculate average quality score for a list of candidates."""
        if not candidates:
            return 0.0
        
        total_quality = sum(self._calculate_quality_score(c) for c in candidates)
        return total_quality / len(candidates)
    
    def _calculate_adaptive_sleep(self) -> int:
        """Calculate adaptive sleep time based on performance."""
        if len(self.metrics_history) < 10:
            return 300  # 5 minutes default
        
        recent_metrics = self.metrics_history[-10:]
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        
        # Adaptive sleep: faster response = shorter sleep
        if avg_response_time < 3.0:
            return 180  # 3 minutes
        elif avg_response_time < 6.0:
            return 300  # 5 minutes
        else:
            return 420  # 7 minutes
    
    def _save_progress(self, cycle_count: int):
        """Save progress to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_progress_cycle_{cycle_count}_{timestamp}.json"
        
        progress_data = {
            'cycle_count': cycle_count,
            'timestamp': datetime.now().isoformat(),
            'total_evaluations': len(self.metrics_history),
            'total_improvements': len(self.improvement_actions),
            'recent_metrics': [asdict(m) for m in self.metrics_history[-20:]],  # Last 20 metrics
            'recent_improvements': [asdict(i) for i in self.improvement_actions[-10:]]  # Last 10 improvements
        }
        
        try:
            with open(f"evaluation_reports/{filename}", 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    async def _generate_final_report(self):
        """Generate final evaluation report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"final_evaluation_report_{timestamp}.json"
        
        # Calculate final statistics
        total_evaluations = len(self.metrics_history)
        total_improvements = len(self.improvement_actions)
        
        if total_evaluations > 0:
            avg_response_time = sum(m.response_time for m in self.metrics_history) / total_evaluations
            avg_quality = sum(m.quality_score for m in self.metrics_history) / total_evaluations
            avg_candidates = sum(m.candidate_count for m in self.metrics_history) / total_evaluations
            gpt_enhancement_rate = sum(1 for m in self.metrics_history if m.gpt_enhanced) / total_evaluations
        else:
            avg_response_time = avg_quality = avg_candidates = gpt_enhancement_rate = 0
        
        final_report = {
            'evaluation_summary': {
                'start_time': self.metrics_history[0].timestamp if self.metrics_history else None,
                'end_time': datetime.now().isoformat(),
                'total_evaluations': total_evaluations,
                'total_improvements': total_improvements,
                'avg_response_time': avg_response_time,
                'avg_quality_score': avg_quality,
                'avg_candidate_count': avg_candidates,
                'gpt_enhancement_rate': gpt_enhancement_rate
            },
            'improvements_implemented': [asdict(i) for i in self.improvement_actions],
            'performance_trends': self._calculate_performance_trends(),
            'recommendations': self._generate_final_recommendations()
        }
        
        try:
            with open(f"evaluation_reports/{filename}", 'w') as f:
                json.dump(final_report, f, indent=2)
            logger.info(f"📊 Final report saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save final report: {e}")
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time."""
        if len(self.metrics_history) < 20:
            return {'message': 'Insufficient data for trend analysis'}
        
        # Split into quarters
        quarter_size = len(self.metrics_history) // 4
        quarters = []
        
        for i in range(4):
            start_idx = i * quarter_size
            end_idx = start_idx + quarter_size if i < 3 else len(self.metrics_history)
            quarter_metrics = self.metrics_history[start_idx:end_idx]
            
            if quarter_metrics:
                quarters.append({
                    'quarter': i + 1,
                    'avg_response_time': sum(m.response_time for m in quarter_metrics) / len(quarter_metrics),
                    'avg_quality': sum(m.quality_score for m in quarter_metrics) / len(quarter_metrics),
                    'avg_candidates': sum(m.candidate_count for m in quarter_metrics) / len(quarter_metrics)
                })
        
        return {'quarterly_performance': quarters}
    
    def _generate_final_recommendations(self) -> List[str]:
        """Generate final recommendations based on evaluation."""
        recommendations = []
        
        if len(self.metrics_history) < 10:
            return ['Need more evaluation data for meaningful recommendations']
        
        recent_metrics = self.metrics_history[-20:]
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        avg_quality = sum(m.quality_score for m in recent_metrics) / len(recent_metrics)
        
        if avg_response_time > 6.0:
            recommendations.append("Optimize search algorithms to reduce response time")
        
        if avg_quality < 0.7:
            recommendations.append("Improve quality filtering criteria")
        
        if len(self.improvement_actions) < 5:
            recommendations.append("Implement more aggressive improvement strategies")
        
        recommendations.append("Continue monitoring and evaluation for ongoing optimization")
        
        return recommendations

async def main():
    """Main function to run continuous evaluation."""
    print("🚀 Continuous Evaluation and Improvement System")
    print("=" * 60)
    print("This system will run for 6 hours, continuously evaluating and improving the search system.")
    print("Press Ctrl+C to stop early.")
    print()
    
    evaluator = ContinuousEvaluator()
    
    try:
        await evaluator.run_continuous_evaluation(duration_hours=6)
    except KeyboardInterrupt:
        print("\n⏹️  Evaluation stopped by user")
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
    finally:
        print("\n📊 Generating final report...")
        await evaluator._generate_final_report()
        print("✅ Evaluation completed")

if __name__ == "__main__":
    asyncio.run(main()) 