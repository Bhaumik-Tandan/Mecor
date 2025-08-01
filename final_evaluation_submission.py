#!/usr/bin/env python3
"""
Final Evaluation Submission Script
==================================
Compiles all results and submits to the evaluation API for final grading.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import SearchAgent
from src.services.evaluation_service import evaluation_service
from src.config.settings import config
from src.utils.logger import get_logger, setup_logger

logger = setup_logger(
    name="final_evaluation",
    level="INFO",
    log_file="logs/final_evaluation.log"
)

class FinalEvaluationSubmission:
    """Comprehensive final evaluation and submission."""
    
    def __init__(self):
        self.search_agent = SearchAgent()
        self.target_score = 30.0
        logger.info("🎯 Initialized Final Evaluation Submission")
    
    def get_current_progress(self) -> Dict[str, Any]:
        """Get current progress from iterative improvement."""
        try:
            progress_file = Path("results/iterative_progress.json")
            if progress_file.exists():
                with open(progress_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error reading progress: {e}")
            return {}
    
    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run final comprehensive evaluation across all categories."""
        logger.info("🏆 Running final comprehensive evaluation")
        
        try:
            results = self.search_agent.run_evaluation()
            
            # Extract scores from results
            scores = {}
            eval_results = results.get("evaluation_results", {})
            
            for category, eval_result in eval_results.items():
                if eval_result and hasattr(eval_result, 'average_final_score'):
                    scores[category] = eval_result.average_final_score
                else:
                    scores[category] = 0.0
            
            logger.info(f"✅ Final evaluation completed: {len(scores)} categories")
            return results
            
        except Exception as e:
            logger.error(f"❌ Final evaluation failed: {e}")
            return {}
    
    def compile_comprehensive_results(self) -> Dict[str, Any]:
        """Compile comprehensive results for final submission."""
        logger.info("📊 Compiling comprehensive results")
        
        # Get current progress
        progress = self.get_current_progress()
        
        # Run final evaluation
        final_results = self.run_comprehensive_evaluation()
        
        # Compile comprehensive data
        comprehensive_results = {
            "submission_info": {
                "timestamp": datetime.now().isoformat(),
                "author": "Bhaumik Tandan",
                "email": "bhaumik.tandan@gmail.com",
                "target_score": self.target_score,
                "submission_type": "iterative_improvement_final"
            },
            "iterative_progress": progress,
            "final_evaluation_results": final_results,
            "performance_summary": {},
            "category_details": {},
            "submission_ready": True
        }
        
        # Extract final scores
        final_scores = {}
        if final_results and "evaluation_results" in final_results:
            for category, eval_result in final_results["evaluation_results"].items():
                if eval_result and hasattr(eval_result, 'average_final_score'):
                    final_scores[category] = eval_result.average_final_score
                else:
                    final_scores[category] = 0.0
        
        # Performance analysis
        categories_above_target = sum(1 for score in final_scores.values() if score >= self.target_score)
        avg_score = sum(final_scores.values()) / len(final_scores) if final_scores else 0
        
        comprehensive_results["performance_summary"] = {
            "total_categories": len(final_scores),
            "categories_above_target": categories_above_target,
            "success_rate_percentage": (categories_above_target / len(final_scores)) * 100 if final_scores else 0,
            "average_score": avg_score,
            "best_score": max(final_scores.values()) if final_scores else 0,
            "worst_score": min(final_scores.values()) if final_scores else 0,
            "final_scores": final_scores,
            "categories_above_30": [cat for cat, score in final_scores.items() if score >= 30],
            "categories_below_30": [cat for cat, score in final_scores.items() if score < 30]
        }
        
        # Category details for submission
        for category in config.job_categories:
            score = final_scores.get(category, 0.0)
            comprehensive_results["category_details"][category] = {
                "final_score": score,
                "meets_target": score >= self.target_score,
                "category_clean": category.replace("_", " ").replace(".yml", ""),
                "status": "✅ PASS" if score >= self.target_score else "❌ NEEDS_IMPROVEMENT"
            }
        
        return comprehensive_results
    
    def submit_to_evaluation_api(self, comprehensive_results: Dict[str, Any]) -> Dict[str, Any]:
        """Submit all categories to evaluation API for final grading."""
        logger.info("🚀 Submitting all categories to evaluation API")
        
        final_scores = comprehensive_results["performance_summary"]["final_scores"]
        
        # Prepare all evaluations for submission
        evaluations = []
        for category in config.job_categories:
            # Get candidates for each category
            from src.models.candidate import SearchQuery, SearchStrategy
            
            query = SearchQuery(
                query_text=category.replace("_", " ").replace(".yml", ""),
                job_category=category,
                strategy=SearchStrategy.HYBRID,
                max_candidates=100
            )
            
            candidates = self.search_agent.search_service.search_candidates(query, SearchStrategy.HYBRID)
            if candidates:
                candidate_ids = [c.id for c in candidates[:10]]  # Top 10 for evaluation
                evaluations.append({
                    "config_name": category,
                    "candidate_ids": candidate_ids
                })
                logger.info(f"✅ Prepared {category}: {len(candidate_ids)} candidates")
        
        # Submit all evaluations
        logger.info(f"📡 Submitting {len(evaluations)} categories for final grading")
        api_results = evaluation_service.evaluate_multiple_configs(evaluations)
        
        # Process API results
        submission_results = {
            "api_submission_timestamp": datetime.now().isoformat(),
            "categories_submitted": len(evaluations),
            "api_responses": {},
            "final_grades": {},
            "overall_performance": {}
        }
        
        final_api_scores = {}
        for category, result in api_results.items():
            if result:
                score = result.average_final_score
                final_api_scores[category] = score
                submission_results["api_responses"][category] = {
                    "score": score,
                    "num_candidates": result.num_candidates,
                    "status": "success"
                }
                submission_results["final_grades"][category] = {
                    "score": score,
                    "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 30 else "F",
                    "meets_requirement": score >= self.target_score
                }
            else:
                submission_results["api_responses"][category] = {
                    "score": 0.0,
                    "status": "failed"
                }
                submission_results["final_grades"][category] = {
                    "score": 0.0,
                    "grade": "F",
                    "meets_requirement": False
                }
        
        # Overall performance
        if final_api_scores:
            categories_passing = sum(1 for score in final_api_scores.values() if score >= self.target_score)
            avg_final_score = sum(final_api_scores.values()) / len(final_api_scores)
            
            submission_results["overall_performance"] = {
                "total_categories": len(final_api_scores),
                "categories_passing": categories_passing,
                "pass_rate_percentage": (categories_passing / len(final_api_scores)) * 100,
                "average_final_score": avg_final_score,
                "highest_score": max(final_api_scores.values()),
                "lowest_score": min(final_api_scores.values()),
                "overall_grade": "EXCELLENT" if avg_final_score >= 70 else "GOOD" if avg_final_score >= 50 else "SATISFACTORY" if avg_final_score >= 30 else "NEEDS_IMPROVEMENT"
            }
        
        return submission_results
    
    def save_final_results(self, comprehensive_results: Dict[str, Any], submission_results: Dict[str, Any]):
        """Save all final results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save comprehensive results
        final_data = {
            "comprehensive_results": comprehensive_results,
            "api_submission_results": submission_results,
            "completion_timestamp": datetime.now().isoformat()
        }
        
        # Save to JSON
        with open(f"results/final_submission_{timestamp}.json", 'w') as f:
            json.dump(final_data, f, indent=2)
        
        # Save summary CSV
        if submission_results.get("final_grades"):
            import csv
            with open(f"results/final_grades_{timestamp}.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Category", "Final_Score", "Grade", "Meets_Requirement", "Status"])
                
                for category, grade_info in submission_results["final_grades"].items():
                    writer.writerow([
                        category,
                        grade_info["score"],
                        grade_info["grade"],
                        grade_info["meets_requirement"],
                        "PASS" if grade_info["meets_requirement"] else "FAIL"
                    ])
        
        logger.info(f"💾 Final results saved with timestamp: {timestamp}")
        return timestamp
    
    def generate_final_report(self, comprehensive_results: Dict[str, Any], submission_results: Dict[str, Any]) -> str:
        """Generate final human-readable report."""
        lines = [
            "🎯 FINAL EVALUATION SUBMISSION REPORT",
            "=" * 60,
            f"📅 Submission Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"👤 Author: Bhaumik Tandan (bhaumik.tandan@gmail.com)",
            f"🎯 Target Score: {self.target_score}",
            "",
            "📊 OVERALL PERFORMANCE:",
            "-" * 40
        ]
        
        if submission_results.get("overall_performance"):
            perf = submission_results["overall_performance"]
            lines.extend([
                f"📈 Average Final Score: {perf['average_final_score']:.2f}",
                f"✅ Categories Passing (≥30): {perf['categories_passing']}/{perf['total_categories']}",
                f"📊 Pass Rate: {perf['pass_rate_percentage']:.1f}%",
                f"🏆 Highest Score: {perf['highest_score']:.2f}",
                f"📉 Lowest Score: {perf['lowest_score']:.2f}",
                f"🎖️ Overall Grade: {perf['overall_grade']}",
                ""
            ])
        
        lines.extend([
            "📋 CATEGORY BREAKDOWN:",
            "-" * 40
        ])
        
        if submission_results.get("final_grades"):
            # Sort by score descending
            sorted_grades = sorted(
                submission_results["final_grades"].items(),
                key=lambda x: x[1]["score"],
                reverse=True
            )
            
            for category, grade_info in sorted_grades:
                status_emoji = "✅" if grade_info["meets_requirement"] else "❌"
                lines.append(f"{status_emoji} {category:<35}: {grade_info['score']:>8.2f} ({grade_info['grade']})")
        
        return "\n".join(lines)
    
    def execute_final_submission(self) -> bool:
        """Execute complete final submission process."""
        try:
            logger.info("🚀 Starting final submission process")
            
            # Step 1: Compile comprehensive results
            logger.info("📊 Step 1: Compiling comprehensive results")
            comprehensive_results = self.compile_comprehensive_results()
            
            # Step 2: Submit to API
            logger.info("📡 Step 2: Submitting to evaluation API")
            submission_results = self.submit_to_evaluation_api(comprehensive_results)
            
            # Step 3: Save results
            logger.info("💾 Step 3: Saving final results")
            timestamp = self.save_final_results(comprehensive_results, submission_results)
            
            # Step 4: Generate report
            logger.info("📋 Step 4: Generating final report")
            final_report = self.generate_final_report(comprehensive_results, submission_results)
            
            # Display results
            print("\n" + "=" * 60)
            print(final_report)
            print("=" * 60)
            print(f"📁 Detailed results saved to: results/final_submission_{timestamp}.json")
            print(f"📊 Grade summary saved to: results/final_grades_{timestamp}.csv")
            print("=" * 60)
            
            # Success criteria
            if submission_results.get("overall_performance"):
                pass_rate = submission_results["overall_performance"]["pass_rate_percentage"]
                avg_score = submission_results["overall_performance"]["average_final_score"]
                
                if pass_rate >= 100:
                    print("🎉 PERFECT SUCCESS! All categories above 30!")
                elif pass_rate >= 80:
                    print("🏆 EXCELLENT! Most categories passing!")
                elif avg_score >= 30:
                    print("✅ GOOD! Average score meets target!")
                else:
                    print("📈 PROGRESS MADE! Continue improving!")
            
            logger.info("✅ Final submission process completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Final submission failed: {e}", exc_info=True)
            print(f"❌ Error during final submission: {e}")
            return False


def main():
    """Main entry point."""
    try:
        print("🚀 Starting Final Evaluation Submission")
        print("=" * 60)
        print("📊 Compiling all results and submitting to evaluation API")
        print("🎯 Target: All categories ≥ 30.0")
        print("=" * 60)
        
        submitter = FinalEvaluationSubmission()
        success = submitter.execute_final_submission()
        
        if success:
            print("\n🎉 Final submission completed successfully!")
        else:
            print("\n❌ Final submission encountered issues. Check logs for details.")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Final submission interrupted by user")
        print("\n⚠️ Submission interrupted by user")
    except Exception as e:
        logger.error(f"❌ Final submission failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 