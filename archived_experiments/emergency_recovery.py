#!/usr/bin/env python3
"""
Emergency Recovery Script
========================
Minimal API usage to prevent further score regression.
Only target the absolute worst categories with extreme rate limiting.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agents.validation_agent import IntelligentValidationAgent
from src.services.evaluation_service import evaluation_service
from src.models.candidate import SearchQuery, SearchStrategy
from src.utils.logger import setup_logger

logger = setup_logger(
    name="emergency",
    level="INFO",
    log_file="logs/emergency_recovery.log"
)

class EmergencyRecovery:
    """Emergency recovery with minimal API usage."""
    
    def __init__(self):
        self.validator = IntelligentValidationAgent()
        self.target_score = 30.0
        
        # EXTREME rate limiting to prevent further damage
        self.ultra_safe_delay = 300  # 5 minutes between API calls
        self.search_delay = 60      # 1 minute between searches
        
        logger.info("🚨 Emergency Recovery: Minimal API usage to prevent score loss")
        print("🚨 EMERGENCY RECOVERY MODE")
        print("=" * 50)
        print("⚠️  CRITICAL: Preventing further score regression")
        print("⏳ Using ULTRA-SAFE delays (5 min between API calls)")
        print("🎯 Only targeting worst 1-2 categories")
        print("=" * 50)
    
    def ultra_safe_api_call(self, category: str, candidate_ids: list) -> Optional[float]:
        """Ultra-safe API call with extreme delays."""
        print(f"\n🚨 ULTRA-SAFE API CALL: {category}")
        print("⏳ Waiting 5 minutes to absolutely ensure no rate limits...")
        
        # 5 minute delay before ANY API call
        for remaining in range(self.ultra_safe_delay, 0, -30):
            print(f"⏱️ {remaining//60}:{remaining%60:02d} remaining...")
            time.sleep(30)
        
        try:
            logger.info(f"🔄 Ultra-safe evaluation attempt: {category}")
            eval_result = evaluation_service.evaluate_candidates(category, candidate_ids)
            
            if eval_result and eval_result.average_final_score is not None:
                score = eval_result.average_final_score
                logger.info(f"✅ {category}: Ultra-safe call successful = {score:.2f}")
                print(f"✅ {category}: {score:.2f}")
                return score
            else:
                logger.warning(f"⚠️ {category}: No result from ultra-safe call")
                print(f"⚠️ {category}: No result returned")
                return None
                
        except Exception as e:
            logger.error(f"❌ {category}: Ultra-safe call failed: {e}")
            print(f"❌ {category}: Failed even with ultra-safe approach: {e}")
            return None
    
    def get_current_status_from_files(self) -> Dict[str, float]:
        """Get current status from existing result files to avoid API calls."""
        print("\n📄 Reading current status from files (no API calls)...")
        
        # Check multiple potential score files
        score_files = [
            "results/evaluation_results.csv",
            "results/detailed_results.json",
            "results/iterative_progress.json",
            "results/focused_progress.json"
        ]
        
        latest_scores = {}
        
        for file_path in score_files:
            if not Path(file_path).exists():
                continue
                
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Try different JSON structures
                    if "current_scores" in data:
                        latest_scores.update(data["current_scores"])
                        print(f"📊 Found scores in {file_path}")
                    elif "scores" in data:
                        latest_scores.update(data["scores"])
                        print(f"📊 Found scores in {file_path}")
                        
                elif file_path.endswith('.csv'):
                    # Read CSV format
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    
                    for line in lines[1:]:  # Skip header
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            category = parts[0]
                            try:
                                score = float(parts[1])
                                latest_scores[category] = score
                            except:
                                continue
                    
                    if latest_scores:
                        print(f"📊 Found scores in {file_path}")
                        
            except Exception as e:
                logger.warning(f"⚠️ Could not read {file_path}: {e}")
                continue
        
        return latest_scores
    
    def emergency_single_category_fix(self, category: str, current_score: float) -> Optional[float]:
        """Emergency fix for ONE category with ultra-safe approach."""
        print(f"\n🚨 EMERGENCY FIX: {category}")
        print(f"📊 Current: {current_score:.2f}")
        print(f"🎯 Target: {self.target_score:.2f} (needs +{self.target_score - current_score:.2f})")
        print("-" * 50)
        
        # Ultra-targeted search strategy
        search_strategies = {
            "doctors_md.yml": "Harvard Medical School physician MD degree board certified",
            "quantitative_finance.yml": "Goldman Sachs quantitative analyst mathematical finance",
            "anthropology.yml": "Harvard anthropology PhD cultural research",
            "biology_expert.yml": "MIT biology PhD molecular research",
            "mathematics_phd.yml": "Stanford mathematics PhD research",
            "bankers.yml": "Goldman Sachs investment banking analyst",
            "mechanical_engineers.yml": "MIT mechanical engineering degree",
            "tax_lawyer.yml": "Harvard Law tax attorney JD degree",
            "radiology.yml": "Johns Hopkins radiology resident MD",
            "junior_corporate_lawyer.yml": "Harvard Law corporate attorney associate"
        }
        
        query_text = search_strategies.get(category, category.replace("_", " ").replace(".yml", ""))
        
        print(f"🔍 Ultra-targeted search: {query_text}")
        print("⏳ Waiting 1 minute before search...")
        time.sleep(self.search_delay)
        
        try:
            query = SearchQuery(
                query_text=query_text,
                job_category=category,
                strategy=SearchStrategy.HYBRID,
                max_candidates=50  # Very conservative
            )
            
            session_id = f"emergency_{category}_{int(time.time())}"
            candidates, _ = self.validator.orchestrate_search(query, session_id)
            
            if not candidates:
                print(f"❌ No candidates found for {category}")
                return None
            
            # Take only top 5 candidates for evaluation
            candidate_ids = [c.id for c in candidates[:5]]
            print(f"📋 Found {len(candidates)} candidates, evaluating top 5...")
            
            # Ultra-safe API call
            score = self.ultra_safe_api_call(category, candidate_ids)
            return score
            
        except Exception as e:
            logger.error(f"❌ Emergency search failed for {category}: {e}")
            print(f"❌ Emergency search failed: {e}")
            return None
    
    def run_emergency_recovery(self):
        """Run emergency recovery targeting only worst categories."""
        logger.info("🚨 Starting emergency recovery")
        
        print("\n🚨 EMERGENCY RECOVERY PROTOCOL")
        print("=" * 60)
        
        # Get current status from files (no API calls)
        current_scores = self.get_current_status_from_files()
        
        if not current_scores:
            print("❌ No current scores found in files. Cannot proceed safely.")
            return
        
        print(f"\n📊 CURRENT STATUS FROM FILES:")
        print("-" * 40)
        
        problem_categories = []
        passing_categories = []
        
        for category, score in current_scores.items():
            if score < self.target_score:
                deficit = self.target_score - score
                problem_categories.append((category, score, deficit))
                print(f"❌ {category}: {score:.2f} (needs +{deficit:.2f})")
            else:
                passing_categories.append((category, score))
                print(f"✅ {category}: {score:.2f}")
        
        print(f"\n📈 Status: {len(passing_categories)}/10 categories passing")
        
        if len(problem_categories) == 0:
            print("\n🎉 ALL CATEGORIES ABOVE TARGET!")
            return
        
        # Sort by deficit (worst first) and target only the WORST 1-2
        problem_categories.sort(key=lambda x: x[2], reverse=True)
        
        # ONLY target the absolute worst to minimize API usage
        max_targets = 2 if len(problem_categories) > 3 else 1
        targets = problem_categories[:max_targets]
        
        print(f"\n🎯 EMERGENCY TARGETS (max {max_targets}):")
        for category, score, deficit in targets:
            print(f"🚨 {category}: {score:.2f} (deficit: -{deficit:.2f})")
        
        print(f"\n⚠️  WARNING: Only targeting worst {len(targets)} to prevent rate limits")
        print("⏳ This will take a LONG time with ultra-safe delays")
        
        input("\n⏸️  Press ENTER to confirm emergency recovery or Ctrl+C to cancel...")
        
        # Emergency fix for each target
        for i, (category, current_score, deficit) in enumerate(targets):
            print(f"\n" + "=" * 60)
            print(f"🚨 EMERGENCY TARGET {i + 1}/{len(targets)}: {category}")
            print("=" * 60)
            
            new_score = self.emergency_single_category_fix(category, current_score)
            
            if new_score is not None and new_score >= self.target_score:
                print(f"🎉 SUCCESS: {category} reached target!")
                logger.info(f"🎉 Emergency fix successful: {category} = {new_score:.2f}")
            elif new_score is not None:
                improvement = new_score - current_score
                print(f"📈 Progress: {category} improved by +{improvement:.2f}")
            else:
                print(f"❌ Emergency fix failed for {category}")
        
        print("\n" + "=" * 60)
        print("🚨 EMERGENCY RECOVERY COMPLETE")
        print("⚠️  Recommend waiting 1+ hours before any more API calls")
        print("=" * 60)


def main():
    """Main entry point."""
    try:
        recovery = EmergencyRecovery()
        recovery.run_emergency_recovery()
        
    except KeyboardInterrupt:
        print("\n⚠️ Emergency recovery cancelled")
    except Exception as e:
        print(f"❌ Emergency recovery error: {e}")


if __name__ == "__main__":
    main() 