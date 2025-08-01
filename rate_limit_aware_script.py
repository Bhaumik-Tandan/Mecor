#!/usr/bin/env python3
"""
Rate Limit Aware Improvement Script
===================================
Properly respects Mercor API rate limits with intelligent backoff.
Based on Mercor take-home guidelines and 429 error patterns.
"""

import sys
import time
import random
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import SearchAgent
from src.agents.validation_agent import IntelligentValidationAgent
from src.services.evaluation_service import evaluation_service
from src.models.candidate import SearchQuery, SearchStrategy
from src.utils.logger import get_logger, setup_logger

logger = setup_logger(
    name="rate_aware",
    level="INFO",
    log_file="logs/rate_aware.log"
)

class RateLimitAwareImprovement:
    """Improvement script that properly respects API rate limits."""
    
    def __init__(self):
        self.search_agent = SearchAgent()
        self.validator = IntelligentValidationAgent()
        self.target_score = 30.0
        
        # Rate limiting configuration based on 429 error patterns
        self.base_delay = 45  # Base delay between API calls (45 seconds)
        self.rate_limit_backoff = 180  # 3 minutes backoff on 429
        self.max_backoff = 600  # Maximum 10 minutes backoff
        self.jitter_range = 10  # Random jitter to avoid thundering herd
        
        # API call tracking
        self.last_api_call = 0
        self.consecutive_429s = 0
        
        logger.info("🛡️ Rate Limit Aware Script: Respecting Mercor API limits")
        print("🛡️ RATE LIMIT AWARE IMPROVEMENT")
        print("=" * 50)
        print("⏳ Using conservative delays to respect API limits")
        print("🔄 Intelligent backoff on 429 errors")
        print("🎯 Goal: ALL categories above 30 (safely)")
        print("=" * 50)
    
    def smart_delay(self, operation_type: str = "api_call"):
        """Smart delay that respects rate limits."""
        current_time = time.time()
        
        if operation_type == "api_call":
            # Ensure minimum delay between API calls
            time_since_last = current_time - self.last_api_call
            min_delay = self.base_delay + (self.consecutive_429s * 30)  # Increase delay after 429s
            
            if time_since_last < min_delay:
                wait_time = min_delay - time_since_last
                # Add jitter to avoid synchronized requests
                wait_time += random.uniform(0, self.jitter_range)
                
                logger.info(f"⏱️ Rate limit delay: {wait_time:.1f}s (429 count: {self.consecutive_429s})")
                print(f"⏱️ Waiting {wait_time:.1f}s to respect rate limits...")
                time.sleep(wait_time)
            
            self.last_api_call = time.time()
        
        elif operation_type == "search":
            # Shorter delay for search operations
            time.sleep(5 + random.uniform(0, 3))
    
    def safe_api_call(self, category: str, candidate_ids: list, max_retries: int = 3) -> Optional[float]:
        """Safe API call with intelligent backoff on 429 errors."""
        for attempt in range(max_retries):
            try:
                # Smart delay before API call
                self.smart_delay("api_call")
                
                logger.info(f"📊 API call attempt {attempt + 1}/{max_retries} for {category}")
                print(f"📊 Evaluating {category} (attempt {attempt + 1}/{max_retries})...")
                
                eval_result = evaluation_service.evaluate_candidates(category, candidate_ids)
                
                if eval_result and eval_result.average_final_score is not None:
                    score = eval_result.average_final_score
                    logger.info(f"✅ {category}: API call successful, score = {score:.2f}")
                    print(f"✅ {category}: {score:.2f}")
                    
                    # Reset 429 counter on success
                    self.consecutive_429s = 0
                    return score
                else:
                    logger.warning(f"⚠️ {category}: API returned no result")
                    
            except Exception as e:
                error_str = str(e)
                
                if "429" in error_str or "Too Many Requests" in error_str:
                    self.consecutive_429s += 1
                    backoff_time = min(
                        self.rate_limit_backoff * (2 ** (self.consecutive_429s - 1)),
                        self.max_backoff
                    )
                    # Add jitter
                    backoff_time += random.uniform(0, 30)
                    
                    logger.warning(f"🚫 429 Rate limit hit for {category} (count: {self.consecutive_429s})")
                    print(f"🚫 Rate limited! Backing off for {backoff_time:.1f}s...")
                    
                    if attempt < max_retries - 1:  # Don't wait on last attempt
                        time.sleep(backoff_time)
                else:
                    logger.error(f"❌ {category} API error (attempt {attempt + 1}): {e}")
                    time.sleep(30)  # Short delay for other errors
        
        logger.error(f"❌ {category}: All API attempts failed")
        print(f"❌ {category}: API calls failed after {max_retries} attempts")
        return None
    
    def safe_search_and_evaluate(self, category: str, query_text: str, strategy: SearchStrategy) -> Optional[float]:
        """Safely search and evaluate with rate limiting."""
        try:
            print(f"\n🔍 Searching: {category}")
            print(f"📝 Query: {query_text}")
            print(f"🔧 Strategy: {strategy.value}")
            
            # Smart delay before search
            self.smart_delay("search")
            
            query = SearchQuery(
                query_text=query_text,
                job_category=category,
                strategy=strategy,
                max_candidates=200  # Conservative candidate count
            )
            
            session_id = f"rate_safe_{category}_{int(time.time())}"
            candidates, _ = self.validator.orchestrate_search(query, session_id)
            
            if not candidates:
                logger.warning(f"⚠️ No candidates found for {category}")
                print(f"⚠️ No candidates found for {category}")
                return None
            
            # Take top 10 candidates for evaluation
            candidate_ids = [c.id for c in candidates[:10]]
            logger.info(f"📋 {category}: Found {len(candidates)} candidates, evaluating top 10")
            print(f"📋 Found {len(candidates)} candidates, evaluating top 10...")
            
            # Safe API call with rate limiting
            score = self.safe_api_call(category, candidate_ids)
            return score
            
        except Exception as e:
            logger.error(f"❌ Search/evaluation failed for {category}: {e}")
            print(f"❌ Search failed for {category}: {e}")
            return None
    
    def get_current_scores_safely(self) -> Dict[str, float]:
        """Get current scores with proper rate limiting."""
        print("\n🔍 Getting current scores safely...")
        logger.info("📊 Starting safe score retrieval")
        
        try:
            # Use a very conservative delay before full evaluation
            print("⏱️ Preparing for full evaluation with rate limiting...")
            time.sleep(60)  # 1 minute delay before starting
            
            eval_result = self.search_agent.run_evaluation()
            
            if eval_result and hasattr(eval_result, 'results'):
                scores = {}
                for category, result in eval_result.results.items():
                    if result and hasattr(result, 'average_final_score'):
                        scores[category] = result.average_final_score
                    else:
                        scores[category] = 0.0
                
                logger.info(f"📊 Retrieved scores for {len(scores)} categories")
                return scores
            else:
                logger.error("❌ Failed to get evaluation results")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Failed to get current scores: {e}")
            print(f"❌ Failed to get current scores: {e}")
            return {}
    
    def improve_category_safely(self, category: str, current_score: float) -> float:
        """Improve a single category with rate limiting."""
        print(f"\n🎯 IMPROVING: {category}")
        print(f"📊 Current score: {current_score:.2f}")
        print(f"🎯 Target: {self.target_score:.2f} (needs +{self.target_score - current_score:.2f})")
        print("-" * 50)
        
        best_score = current_score
        
        # Define targeted strategies for each category
        strategies = {
            "doctors_md.yml": [
                ("Harvard Medical School Johns Hopkins Mayo Clinic physician MD degree", SearchStrategy.HYBRID),
                ("board certified doctor residency fellowship medicine", SearchStrategy.VECTOR_ONLY),
                ("medical degree physician surgeon specialist", SearchStrategy.BM25_ONLY)
            ],
            "quantitative_finance.yml": [
                ("Goldman Sachs JPMorgan quantitative analyst trader", SearchStrategy.HYBRID),
                ("mathematical finance PhD derivatives pricing risk", SearchStrategy.VECTOR_ONLY),
                ("quantitative research financial engineering", SearchStrategy.BM25_ONLY)
            ],
            "anthropology.yml": [
                ("cultural anthropology research ethnography field work", SearchStrategy.HYBRID),
                ("anthropologist social sciences Harvard Yale Stanford", SearchStrategy.VECTOR_ONLY),
                ("anthropology PhD dissertation cultural studies", SearchStrategy.BM25_ONLY)
            ],
            "biology_expert.yml": [
                ("molecular biology PhD Harvard MIT Stanford", SearchStrategy.HYBRID),
                ("biologist research scientist biotechnology", SearchStrategy.VECTOR_ONLY),
                ("biology degree genetics microbiology", SearchStrategy.BM25_ONLY)
            ]
        }
        
        # Get strategies for this category (or default)
        category_strategies = strategies.get(category, [
            (category.replace("_", " ").replace(".yml", ""), SearchStrategy.HYBRID),
            (f"{category.replace('_', ' ').replace('.yml', '')} expert professional", SearchStrategy.VECTOR_ONLY)
        ])
        
        for i, (query_text, strategy) in enumerate(category_strategies):
            print(f"\n🔧 Strategy {i + 1}/{len(category_strategies)}: {strategy.value}")
            
            score = self.safe_search_and_evaluate(category, query_text, strategy)
            
            if score is not None and score > best_score:
                best_score = score
                improvement = score - current_score
                print(f"✅ Improvement! {current_score:.2f} → {score:.2f} (+{improvement:.2f})")
                logger.info(f"✅ {category}: Strategy {i + 1} improved score to {score:.2f}")
                
                if score >= self.target_score:
                    print(f"🎉 {category}: TARGET REACHED! {score:.2f} >= {self.target_score}")
                    logger.info(f"🎉 {category}: Target reached!")
                    return score
            
            # Delay between strategies to avoid overwhelming API
            if i < len(category_strategies) - 1:
                delay = 30 + random.uniform(0, 15)
                print(f"⏱️ Strategy delay: {delay:.1f}s...")
                time.sleep(delay)
        
        improvement = best_score - current_score
        print(f"\n📊 {category}: Best achieved: {best_score:.2f} (+{improvement:.2f})")
        logger.info(f"📊 {category}: Final score {best_score:.2f} (+{improvement:.2f})")
        
        return best_score
    
    def run_rate_aware_improvement(self) -> bool:
        """Run improvement with full rate limiting awareness."""
        logger.info("🚀 Starting rate-aware improvement")
        
        print("\n🚀 STARTING RATE-AWARE IMPROVEMENT")
        print("=" * 60)
        
        # Get current scores safely
        current_scores = self.get_current_scores_safely()
        
        if not current_scores:
            print("❌ Could not get current scores. Exiting.")
            return False
        
        # Identify categories below target
        problem_categories = []
        passing_categories = []
        
        for category, score in current_scores.items():
            if score < self.target_score:
                deficit = self.target_score - score
                problem_categories.append((category, score, deficit))
            else:
                passing_categories.append((category, score))
        
        # Sort by deficit (worst first)
        problem_categories.sort(key=lambda x: x[2], reverse=True)
        
        print(f"\n📊 CURRENT STATUS:")
        print(f"✅ Passing categories: {len(passing_categories)}/10")
        print(f"❌ Need improvement: {len(problem_categories)}/10")
        print(f"📈 Success rate: {len(passing_categories) * 10}%")
        
        if len(problem_categories) == 0:
            print("\n🎉 ALL CATEGORIES ALREADY ABOVE TARGET!")
            return True
        
        print(f"\n🎯 TARGETING {len(problem_categories)} CATEGORIES:")
        for category, score, deficit in problem_categories:
            print(f"❌ {category}: {score:.2f} (needs +{deficit:.2f})")
        
        # Improve each problematic category
        for i, (category, current_score, deficit) in enumerate(problem_categories):
            print(f"\n" + "=" * 60)
            print(f"🎯 CATEGORY {i + 1}/{len(problem_categories)}: {category}")
            print("=" * 60)
            
            new_score = self.improve_category_safely(category, current_score)
            
            if new_score >= self.target_score:
                print(f"✅ SUCCESS: {category} now above target!")
            
            # Long delay between categories to be extra safe
            if i < len(problem_categories) - 1:
                delay = 120 + random.uniform(0, 30)  # 2+ minutes between categories
                print(f"\n⏱️ Category transition delay: {delay:.1f}s...")
                time.sleep(delay)
        
        print("\n" + "=" * 60)
        print("🏆 RATE-AWARE IMPROVEMENT COMPLETE")
        print("=" * 60)
        
        return True


def main():
    """Main entry point."""
    try:
        improver = RateLimitAwareImprovement()
        success = improver.run_rate_aware_improvement()
        
        if success:
            print("\n🎉 Improvement process completed!")
            print("📊 Run final evaluation to check results")
        else:
            print("\n⚠️ Improvement process encountered issues")
            
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 