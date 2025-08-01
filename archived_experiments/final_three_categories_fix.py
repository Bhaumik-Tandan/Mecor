#!/usr/bin/env python3
"""
Final Three Categories Fix
==========================
Target the 3 remaining categories below 30.0:
- biology_expert.yml: 16.00 (needs +14.00)
- quantitative_finance.yml: 8.67 (needs +21.33) 
- doctors_md.yml: 8.00 (needs +22.00)
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import SearchAgent
from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy
from src.utils.logger import setup_logger

logger = setup_logger(
    name="final_three_fix",
    level="INFO",
    log_file="logs/final_three_categories_fix.log"
)

# Target categories with their current scores and deficits
TARGET_CATEGORIES = {
    "biology_expert.yml": {"current": 16.00, "deficit": 14.00},
    "quantitative_finance.yml": {"current": 8.67, "deficit": 21.33},
    "doctors_md.yml": {"current": 8.00, "deficit": 22.00}
}

class FinalThreeFixer:
    def __init__(self):
        self.search_agent = SearchAgent()
        self.evaluation_service = self.search_agent.evaluation_service
        self.max_attempts = 5
        self.base_delay = 60  # 1 minute between API calls
        
    def ultra_safe_delay(self, seconds=None):
        """Ultra-safe delay with countdown."""
        delay = seconds or self.base_delay
        print(f"⏱️ Ultra-safe delay: {delay}s")
        for i in range(delay, 0, -10):
            print(f"   Waiting {i}s...")
            time.sleep(10)
        print("   ✅ Delay complete")
    
    def enhanced_search_strategies(self, category):
        """Multiple enhanced search strategies for difficult categories."""
        
        enhanced_terms = {
            "biology_expert.yml": [
                "molecular biology PhD research scientist",
                "cell biology genetics researcher professor",
                "biomedical research molecular biologist",
                "life sciences PhD postdoc Harvard MIT",
                "computational biology bioinformatics researcher"
            ],
            "quantitative_finance.yml": [
                "quantitative analyst quant finance trader",
                "financial engineering derivatives pricing",
                "algorithmic trading quantitative research",
                "risk management quantitative finance MBA",
                "portfolio optimization financial modeling"
            ],
            "doctors_md.yml": [
                "family medicine physician MD primary care",
                "internal medicine doctor general practitioner",
                "primary care physician family doctor MD",
                "general medicine physician outpatient care",
                "clinical physician family practice MD"
            ]
        }
        
        strategies = []
        
        # Strategy 1: HYBRID with enhanced terms
        for term in enhanced_terms.get(category, [category.replace("_", " ").replace(".yml", "")]):
            strategies.append({
                "type": "HYBRID_ENHANCED",
                "query": term,
                "strategy": SearchStrategy.HYBRID,
                "max_candidates": 200
            })
        
        # Strategy 2: VECTOR_ONLY with broad terms
        strategies.append({
            "type": "VECTOR_BROAD",
            "query": category.replace("_", " ").replace(".yml", "") + " expert professional",
            "strategy": SearchStrategy.VECTOR_ONLY,
            "max_candidates": 150
        })
        
        # Strategy 3: BM25_ONLY with specific keywords
        keyword_terms = {
            "biology_expert.yml": "biology molecular genetics research PhD university",
            "quantitative_finance.yml": "quantitative finance analyst trading derivatives",
            "doctors_md.yml": "doctor physician MD family medicine primary care"
        }
        
        strategies.append({
            "type": "BM25_KEYWORDS",
            "query": keyword_terms.get(category, category.replace("_", " ").replace(".yml", "")),
            "strategy": SearchStrategy.BM25_ONLY,
            "max_candidates": 100
        })
        
        return strategies
    
    def search_with_strategy(self, category, strategy_info):
        """Search with a specific strategy."""
        print(f"🔍 {strategy_info['type']}: {strategy_info['query']}")
        
        query = SearchQuery(
            query_text=strategy_info['query'],
            job_category=category,
            strategy=strategy_info['strategy'],
            max_candidates=strategy_info['max_candidates']
        )
        
        candidates = self.search_agent.search_service.search_candidates(
            query, strategy_info['strategy']
        )
        
        print(f"   Found {len(candidates)} candidates")
        return candidates
    
    def improve_category(self, category, target_info):
        """Improve a single category with multiple strategies."""
        print(f"\n🎯 IMPROVING {category}")
        print(f"   Current: {target_info['current']:.2f}")
        print(f"   Deficit: -{target_info['deficit']:.2f}")
        print("=" * 50)
        
        all_candidates = set()
        strategies = self.enhanced_search_strategies(category)
        
        # Execute all search strategies
        for i, strategy_info in enumerate(strategies, 1):
            print(f"\n🔧 Strategy {i}/{len(strategies)}: {strategy_info['type']}")
            
            try:
                candidates = self.search_with_strategy(category, strategy_info)
                for candidate in candidates:
                    all_candidates.add(candidate.id)
                
                print(f"   Total unique candidates: {len(all_candidates)}")
                
                # Small delay between searches
                time.sleep(5)
                
            except Exception as e:
                print(f"   ❌ Strategy failed: {e}")
                continue
        
        if len(all_candidates) < 10:
            print(f"   ⚠️ Only found {len(all_candidates)} candidates (need 10)")
            return None
        
        # Take top 10 candidates
        candidate_ids = list(all_candidates)[:10]
        print(f"   ✅ Selected {len(candidate_ids)} candidates for evaluation")
        
        # Ultra-safe delay before evaluation
        self.ultra_safe_delay(90)  # 1.5 minutes before evaluation
        
        # Evaluate candidates
        try:
            print(f"📊 Evaluating {category}...")
            result = self.evaluation_service.evaluate_candidates(category, candidate_ids)
            
            if result and hasattr(result, 'average_final_score'):
                new_score = result.average_final_score
                improvement = new_score - target_info['current']
                
                print(f"🎉 NEW SCORE: {new_score:.2f} (improvement: +{improvement:.2f})")
                
                if new_score >= 30.0:
                    print(f"🏆 SUCCESS! {category} reached target!")
                    return {"category": category, "score": new_score, "success": True}
                else:
                    print(f"📈 Progress made, but still below 30.0")
                    return {"category": category, "score": new_score, "success": False}
            else:
                print(f"❌ Evaluation failed for {category}")
                return None
                
        except Exception as e:
            print(f"❌ Evaluation error for {category}: {e}")
            return None
    
    def run_final_improvement(self):
        """Run targeted improvement for all 3 categories."""
        print("🎯 FINAL THREE CATEGORIES IMPROVEMENT")
        print("=" * 60)
        print("Target categories:")
        for cat, info in TARGET_CATEGORIES.items():
            print(f"   {cat}: {info['current']:.2f} (needs +{info['deficit']:.2f})")
        print("=" * 60)
        
        results = []
        successes = 0
        
        # Sort by deficit (easiest first)
        sorted_categories = sorted(
            TARGET_CATEGORIES.items(), 
            key=lambda x: x[1]['deficit']
        )
        
        for category, target_info in sorted_categories:
            print(f"\n🚀 Starting improvement for {category}")
            
            for attempt in range(1, self.max_attempts + 1):
                print(f"\n📍 ATTEMPT {attempt}/{self.max_attempts} for {category}")
                
                result = self.improve_category(category, target_info)
                
                if result:
                    results.append(result)
                    if result['success']:
                        successes += 1
                        print(f"🎊 {category} COMPLETED! Moving to next category.")
                        break
                    else:
                        # Update current score for next attempt
                        target_info['current'] = result['score']
                        target_info['deficit'] = 30.0 - result['score']
                        print(f"🔄 Updated target: {target_info['current']:.2f} (deficit: -{target_info['deficit']:.2f})")
                
                if attempt < self.max_attempts:
                    print(f"⏱️ Preparing for attempt {attempt + 1}...")
                    self.ultra_safe_delay(120)  # 2 minutes between attempts
            
            # Long delay between categories
            if category != sorted_categories[-1][0]:  # Not the last category
                print(f"\n⏱️ Moving to next category...")
                self.ultra_safe_delay(180)  # 3 minutes between categories
        
        # Final summary
        print("\n" + "=" * 60)
        print("🏁 FINAL IMPROVEMENT RESULTS")
        print("=" * 60)
        
        for result in results:
            status = "✅ SUCCESS" if result['success'] else "📈 IMPROVED"
            print(f"{status} {result['category']}: {result['score']:.2f}")
        
        print(f"\n🎯 Categories reaching target: {successes}/3")
        
        if successes == 3:
            print("🎉 ALL CATEGORIES ABOVE 30! MISSION COMPLETE!")
        elif successes > 0:
            print(f"🎊 {successes} categories improved! Progress made!")
        else:
            print("🔄 Continue working on improvements needed.")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"results/final_three_improvement_{timestamp}.json"
        
        summary = {
            "timestamp": timestamp,
            "target_categories": TARGET_CATEGORIES,
            "results": results,
            "successes": successes,
            "total_attempts": len(results)
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"💾 Results saved: {results_file}")

def main():
    """Main execution."""
    try:
        fixer = FinalThreeFixer()
        fixer.run_final_improvement()
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Final three fix failed: {e}")

if __name__ == "__main__":
    main() 