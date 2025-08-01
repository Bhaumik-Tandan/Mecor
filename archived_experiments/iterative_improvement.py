#!/usr/bin/env python3
"""
Iterative Improvement Script
============================
Runs evaluations repeatedly until all scores are above 30.
Uses enhanced validation agents for optimization.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import SearchAgent
from src.agents.enhanced_validation_agent import EnhancedValidationAgent
from src.agents.validation_agent import IntelligentValidationAgent
from src.services.evaluation_service import evaluation_service
from src.utils.logger import get_logger, setup_logger

logger = setup_logger(
    name="iterative_improvement",
    level="INFO",
    log_file="logs/iterative_improvement.log"
)

class IterativeImprovement:
    """Main class for iterative score improvement."""
    
    def __init__(self, target_score: float = 30.0):
        self.target_score = target_score
        self.max_iterations = 10  # Prevent infinite loops
        self.search_agent = SearchAgent()
        self.enhanced_validator = EnhancedValidationAgent()
        self.intelligent_validator = IntelligentValidationAgent()
        
        logger.info(f"🎯 Initialized iterative improvement targeting score >= {target_score}")
    
    def get_current_scores(self) -> Dict[str, float]:
        """Extract current scores from evaluation results."""
        try:
            results_path = Path("results/evaluation_results.csv")
            if not results_path.exists():
                logger.warning("No existing results found, will start fresh")
                return {}
            
            scores = {}
            with open(results_path, 'r') as f:
                lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        category = parts[0]
                        try:
                            score = float(parts[1])
                            scores[category] = score
                        except ValueError:
                            continue
            
            logger.info(f"📊 Current scores loaded: {len(scores)} categories")
            return scores
            
        except Exception as e:
            logger.error(f"Error reading current scores: {e}")
            return {}
    
    def identify_low_scoring_categories(self, scores: Dict[str, float]) -> List[str]:
        """Identify categories with scores below target."""
        low_scoring = [
            category for category, score in scores.items() 
            if score < self.target_score
        ]
        
        logger.info(f"🔍 Found {len(low_scoring)} categories below {self.target_score}")
        for category in low_scoring:
            logger.info(f"   📉 {category}: {scores[category]:.2f}")
        
        return low_scoring
    
    def run_targeted_improvement(self, low_scoring_categories: List[str]) -> Dict[str, float]:
        """Run targeted improvement for specific categories."""
        logger.info(f"🚀 Running targeted improvement for {len(low_scoring_categories)} categories")
        
        # Use intelligent validation agent for iterative improvement
        improved_scores = {}
        
        for category in low_scoring_categories:
            logger.info(f"🔧 Improving {category}")
            
            try:
                # Create search query for this category
                from src.models.candidate import SearchQuery, SearchStrategy
                
                query = SearchQuery(
                    query_text=category.replace("_", " ").replace(".yml", ""),
                    job_category=category,
                    strategy=SearchStrategy.HYBRID,
                    max_candidates=100  # Increased for better results
                )
                
                # Use intelligent validator for orchestrated search with improvement
                best_candidates, validation_results = self.intelligent_validator.orchestrate_search(
                    query, session_id=f"improve_{category}_{int(time.time())}"
                )
                
                if best_candidates:
                    # Evaluate the improved candidates
                    candidate_ids = [c.id for c in best_candidates[:10]]
                    eval_result = evaluation_service.evaluate_candidates(category, candidate_ids)
                    
                    if eval_result:
                        improved_scores[category] = eval_result.average_final_score
                        logger.info(f"✅ {category}: improved to {eval_result.average_final_score:.2f}")
                    else:
                        logger.warning(f"⚠️ {category}: evaluation failed")
                else:
                    logger.warning(f"⚠️ {category}: no candidates found")
                    
            except Exception as e:
                logger.error(f"❌ Error improving {category}: {e}")
        
        return improved_scores
    
    def run_full_evaluation(self) -> Dict[str, float]:
        """Run complete evaluation across all categories."""
        logger.info("🏆 Running full evaluation")
        
        try:
            results = self.search_agent.run_evaluation()
            
            # Extract scores from results
            scores = {}
            eval_results = results.get("evaluation_results", {})
            
            for category, eval_result in eval_results.items():
                if eval_result and hasattr(eval_result, 'average_final_score'):
                    scores[category] = eval_result.average_final_score
            
            logger.info(f"✅ Full evaluation completed: {len(scores)} categories")
            return scores
            
        except Exception as e:
            logger.error(f"❌ Full evaluation failed: {e}")
            return {}
    
    def save_progress(self, iteration: int, scores: Dict[str, float], low_scoring: List[str]):
        """Save current progress to file."""
        progress = {
            "iteration": iteration,
            "timestamp": time.time(),
            "scores": scores,
            "low_scoring_categories": low_scoring,
            "target_score": self.target_score,
            "categories_above_target": len([s for s in scores.values() if s >= self.target_score]),
            "total_categories": len(scores)
        }
        
        progress_file = Path("results/iterative_progress.json")
        with open(progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
        
        logger.info(f"💾 Progress saved: {progress['categories_above_target']}/{progress['total_categories']} above {self.target_score}")
    
    def run_until_target_achieved(self) -> bool:
        """Main method: run evaluations until all scores are above target."""
        logger.info("🎯 Starting iterative improvement process")
        logger.info(f"📌 Target: All scores >= {self.target_score}")
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 ITERATION {iteration}/{self.max_iterations}")
            logger.info(f"{'='*60}")
            
            # Get current scores
            if iteration == 1:
                scores = self.get_current_scores()
                if not scores:
                    # No existing scores, run full evaluation
                    scores = self.run_full_evaluation()
            else:
                # Run full evaluation to get updated scores
                scores = self.run_full_evaluation()
            
            if not scores:
                logger.error("❌ Could not get scores, stopping")
                return False
            
            # Check if target achieved
            low_scoring = self.identify_low_scoring_categories(scores)
            
            if not low_scoring:
                logger.info("🎉 SUCCESS! All scores are above target!")
                logger.info("📊 Final scores:")
                for category, score in sorted(scores.items()):
                    status = "✅" if score >= self.target_score else "❌"
                    logger.info(f"   {status} {category}: {score:.2f}")
                return True
            
            # Save progress
            self.save_progress(iteration, scores, low_scoring)
            
            # Run targeted improvement for low-scoring categories
            if iteration < self.max_iterations:
                logger.info(f"🔧 Attempting to improve {len(low_scoring)} categories")
                improved_scores = self.run_targeted_improvement(low_scoring)
                
                # Update scores with improvements
                scores.update(improved_scores)
                
                logger.info(f"📈 Iteration {iteration} improvements:")
                for category, score in improved_scores.items():
                    status = "✅" if score >= self.target_score else "📈"
                    logger.info(f"   {status} {category}: {score:.2f}")
            
            time.sleep(2)  # Brief pause between iterations
        
        logger.warning(f"⚠️ Maximum iterations ({self.max_iterations}) reached")
        logger.info("📊 Final scores:")
        for category, score in sorted(scores.items()):
            status = "✅" if score >= self.target_score else "❌"
            logger.info(f"   {status} {category}: {score:.2f}")
        
        return len(low_scoring) == 0


def main():
    """Main entry point."""
    try:
        print("🚀 Starting Iterative Improvement Process")
        print("=" * 60)
        print("🎯 Goal: All evaluation scores >= 30.0")
        print("🔧 Using enhanced validation agents for optimization")
        print("=" * 60)
        
        improver = IterativeImprovement(target_score=30.0)
        success = improver.run_until_target_achieved()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 SUCCESS! All scores are now above 30!")
        else:
            print("⚠️ Process completed but some scores may still be below target")
            print("📊 Check results/iterative_progress.json for details")
        print("📁 Results saved to results/ directory")
        print("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("⚠️ Process interrupted by user")
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        logger.error(f"❌ Process failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 