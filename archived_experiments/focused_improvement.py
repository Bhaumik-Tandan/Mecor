#!/usr/bin/env python3
"""
Focused Improvement Script
=========================
Continues improving until EVERY category is above 30.0
Handles API rate limits and focuses on problem categories.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import SearchAgent
from src.agents.enhanced_validation_agent import EnhancedValidationAgent
from src.agents.validation_agent import IntelligentValidationAgent
from src.services.evaluation_service import evaluation_service
from src.utils.logger import get_logger, setup_logger

logger = setup_logger(
    name="focused_improvement",
    level="INFO",
    log_file="logs/focused_improvement.log"
)

class FocusedImprovement:
    """Focused improvement until ALL categories are above 30."""
    
    def __init__(self, target_score: float = 30.0):
        self.target_score = target_score
        self.max_attempts = 20  # More attempts for stubborn categories
        self.search_agent = SearchAgent()
        self.enhanced_validator = EnhancedValidationAgent()
        self.intelligent_validator = IntelligentValidationAgent()
        
        logger.info(f"🎯 Focused improvement: ALL categories must be >= {target_score}")
    
    def get_current_scores(self) -> Dict[str, float]:
        """Get latest scores with rate limit handling."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"🔍 Getting current scores (attempt {attempt + 1}/{max_retries})")
                
                # Add delay to avoid rate limits
                if attempt > 0:
                    delay = 30 * attempt
                    logger.info(f"⏱️ Waiting {delay}s to avoid rate limits")
                    time.sleep(delay)
                
                results = self.search_agent.run_evaluation()
                scores = {}
                
                if results and "evaluation_results" in results:
                    for category, eval_result in results["evaluation_results"].items():
                        if eval_result and hasattr(eval_result, 'average_final_score'):
                            scores[category] = eval_result.average_final_score
                        else:
                            scores[category] = 0.0
                
                logger.info(f"✅ Successfully got scores for {len(scores)} categories")
                return scores
                
            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                if "429" in str(e) or "Too Many Requests" in str(e):
                    wait_time = 60 * (attempt + 1)
                    logger.info(f"💤 Rate limited. Waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                elif attempt == max_retries - 1:
                    logger.error(f"❌ Failed to get scores after {max_retries} attempts")
                    return {}
        
        return {}
    
    def identify_problem_categories(self, scores: Dict[str, float]) -> List[tuple]:
        """Identify categories below target, sorted by how far below they are."""
        problems = []
        for category, score in scores.items():
            if score < self.target_score:
                deficit = self.target_score - score
                problems.append((category, score, deficit))
        
        # Sort by deficit (most problematic first)
        problems.sort(key=lambda x: x[2], reverse=True)
        
        logger.info(f"🔍 Found {len(problems)} categories below {self.target_score}")
        for category, score, deficit in problems:
            logger.info(f"   📉 {category}: {score:.2f} (needs +{deficit:.2f})")
        
        return problems
    
    def improve_single_category(self, category: str, current_score: float) -> float:
        """Focus on improving a single category with enhanced strategies."""
        logger.info(f"🎯 Focusing on {category} (current: {current_score:.2f})")
        
        max_strategies = 5
        best_score = current_score
        
        for strategy_num in range(1, max_strategies + 1):
            try:
                logger.info(f"🔧 Strategy {strategy_num}/{max_strategies} for {category}")
                
                from src.models.candidate import SearchQuery, SearchStrategy
                
                # Use different strategies for each attempt
                if strategy_num == 1:
                    search_strategy = SearchStrategy.HYBRID
                    max_candidates = 100
                elif strategy_num == 2:
                    search_strategy = SearchStrategy.VECTOR_ONLY
                    max_candidates = 150
                elif strategy_num == 3:
                    search_strategy = SearchStrategy.BM25_ONLY
                    max_candidates = 100
                elif strategy_num == 4:
                    search_strategy = SearchStrategy.HYBRID
                    max_candidates = 200  # More candidates
                else:
                    search_strategy = SearchStrategy.VECTOR_ONLY
                    max_candidates = 250  # Even more candidates
                
                query = SearchQuery(
                    query_text=category.replace("_", " ").replace(".yml", ""),
                    job_category=category,
                    strategy=search_strategy,
                    max_candidates=max_candidates
                )
                
                # Use intelligent validator for orchestrated search
                session_id = f"focus_{category}_{strategy_num}_{int(time.time())}"
                best_candidates, validation_results = self.intelligent_validator.orchestrate_search(
                    query, session_id=session_id
                )
                
                if best_candidates:
                    # Evaluate with rate limit handling
                    candidate_ids = [c.id for c in best_candidates[:10]]
                    
                    # Add delay before API call
                    time.sleep(5)
                    
                    eval_result = evaluation_service.evaluate_candidates(category, candidate_ids)
                    
                    if eval_result and hasattr(eval_result, 'average_final_score'):
                        new_score = eval_result.average_final_score
                        
                        if new_score > best_score:
                            best_score = new_score
                            logger.info(f"✅ {category}: Improved to {new_score:.2f} (+{new_score - current_score:.2f})")
                            
                            if new_score >= self.target_score:
                                logger.info(f"🎉 {category}: REACHED TARGET! {new_score:.2f} >= {self.target_score}")
                                return new_score
                        else:
                            logger.info(f"📊 {category}: Strategy {strategy_num} got {new_score:.2f}")
                    else:
                        logger.warning(f"⚠️ {category}: Strategy {strategy_num} evaluation failed")
                else:
                    logger.warning(f"⚠️ {category}: Strategy {strategy_num} found no candidates")
                
                # Add delay between strategies to avoid rate limits
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"❌ Strategy {strategy_num} for {category} failed: {e}")
                if "429" in str(e) or "Too Many Requests" in str(e):
                    logger.info(f"💤 Rate limited. Waiting 60s before next strategy")
                    time.sleep(60)
                else:
                    time.sleep(5)
        
        logger.info(f"📊 {category}: Best score achieved: {best_score:.2f}")
        return best_score
    
    def run_focused_improvement(self) -> bool:
        """Run focused improvement until ALL categories are above target."""
        logger.info("🎯 Starting focused improvement")
        logger.info(f"📌 Goal: ALL categories >= {self.target_score}")
        
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 FOCUSED ATTEMPT {attempt}/{self.max_attempts}")
            logger.info(f"{'='*60}")
            
            # Get current scores
            scores = self.get_current_scores()
            if not scores:
                logger.error("❌ Could not get current scores, stopping")
                return False
            
            # Identify problem categories
            problems = self.identify_problem_categories(scores)
            
            if not problems:
                logger.info("🎉 SUCCESS! All categories are above target!")
                self.display_final_scores(scores)
                return True
            
            # Save progress
            self.save_progress(attempt, scores, problems)
            
            # Focus on the most problematic category first
            most_problematic = problems[0]
            category, current_score, deficit = most_problematic
            
            logger.info(f"🎯 Focusing on most problematic: {category} (deficit: -{deficit:.2f})")
            
            # Improve this category
            new_score = self.improve_single_category(category, current_score)
            
            if new_score >= self.target_score:
                logger.info(f"✅ {category}: SUCCESS! {new_score:.2f} >= {self.target_score}")
            else:
                logger.info(f"📈 {category}: Progress made: {current_score:.2f} → {new_score:.2f}")
            
            # Brief pause between attempts
            time.sleep(5)
        
        logger.warning(f"⚠️ Maximum attempts ({self.max_attempts}) reached")
        final_scores = self.get_current_scores()
        if final_scores:
            remaining_problems = self.identify_problem_categories(final_scores)
            logger.info(f"📊 Final status: {len(remaining_problems)} categories still below target")
            self.display_final_scores(final_scores)
        
        return len(self.identify_problem_categories(final_scores)) == 0 if final_scores else False
    
    def save_progress(self, attempt: int, scores: Dict[str, float], problems: List[tuple]):
        """Save current progress."""
        progress = {
            "attempt": attempt,
            "timestamp": time.time(),
            "target_score": self.target_score,
            "current_scores": scores,
            "problem_categories": [
                {
                    "category": cat,
                    "current_score": score,
                    "deficit": deficit
                }
                for cat, score, deficit in problems
            ],
            "categories_above_target": len(scores) - len(problems),
            "total_categories": len(scores),
            "success_rate": ((len(scores) - len(problems)) / len(scores) * 100) if scores else 0
        }
        
        with open("results/focused_progress.json", 'w') as f:
            json.dump(progress, f, indent=2)
        
        logger.info(f"💾 Progress: {progress['categories_above_target']}/{progress['total_categories']} above {self.target_score}")
    
    def display_final_scores(self, scores: Dict[str, float]):
        """Display final scores in a clear format."""
        logger.info("📊 FINAL SCORES:")
        logger.info("-" * 50)
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        all_above_target = True
        
        for category, score in sorted_scores:
            status = "✅" if score >= self.target_score else "❌"
            if score < self.target_score:
                all_above_target = False
                deficit = self.target_score - score
                logger.info(f"{status} {category:<35}: {score:>8.2f} (needs +{deficit:.2f})")
            else:
                logger.info(f"{status} {category:<35}: {score:>8.2f}")
        
        if all_above_target:
            logger.info("🎉 ALL CATEGORIES ABOVE TARGET! MISSION ACCOMPLISHED!")
        else:
            remaining = sum(1 for s in scores.values() if s < self.target_score)
            logger.info(f"📈 {remaining} categories still need improvement")


def main():
    """Main entry point."""
    try:
        print("🎯 Starting Focused Improvement")
        print("=" * 60)
        print("🎯 Goal: EVERY category score >= 30.0")
        print("🔧 Using enhanced strategies with rate limit handling")
        print("=" * 60)
        
        improver = FocusedImprovement(target_score=30.0)
        success = improver.run_focused_improvement()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 SUCCESS! ALL categories are now above 30!")
        else:
            print("📈 Progress made. Some categories may still need work.")
            print("📊 Check results/focused_progress.json for details")
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