#!/usr/bin/env python3
"""
Fast Improvement - No Rate Limits
=================================
Quick improvement for the 3 remaining categories:
- biology_expert.yml: 19.33 (needs +10.67)
- quantitative_finance.yml: 0.00 (needs +30.00) 
- doctors_md.yml: 15.00 (needs +15.00)
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
    name="fast_improvement",
    level="INFO",
    log_file="logs/fast_improvement_no_limits.log"
)

# Updated target categories with latest scores
TARGET_CATEGORIES = {
    "biology_expert.yml": {"current": 19.33, "deficit": 10.67},
    "quantitative_finance.yml": {"current": 0.00, "deficit": 30.00},
    "doctors_md.yml": {"current": 15.00, "deficit": 15.00}
}

class FastImprover:
    def __init__(self):
        self.search_agent = SearchAgent()
        self.evaluation_service = self.search_agent.evaluation_service
        self.max_attempts = 3  # Reduced attempts for speed
        
    def get_enhanced_search_terms(self, category):
        """Get the most effective search terms for each category."""
        
        premium_terms = {
            "biology_expert.yml": [
                "Harvard MIT Stanford biology professor PhD researcher",
                "Nature Science Cell publication molecular biology",
                "NIH NSF grant principal investigator biology",
                "Johns Hopkins UCSF biology department faculty",
                "postdoc research scientist molecular genetics"
            ],
            "quantitative_finance.yml": [
                "Goldman Sachs JPMorgan quantitative analyst",
                "hedge fund portfolio manager derivatives trader",
                "financial engineering Stanford MIT Wharton MBA",
                "Black-Scholes options pricing risk management",
                "algorithmic trading quantitative research analyst"
            ],
            "doctors_md.yml": [
                "board certified internal medicine physician",
                "Johns Hopkins Mayo Clinic attending physician",
                "family medicine residency primary care MD",
                "clinical medicine hospital physician attending",
                "medical doctor internal medicine practice"
            ]
        }
        
        return premium_terms.get(category, [category.replace("_", " ").replace(".yml", "")])
    
    def fast_search_and_evaluate(self, category, target_info):
        """Fast search and evaluation without delays."""
        print(f"\n🚀 FAST IMPROVING {category}")
        print(f"   Current: {target_info['current']:.2f} | Target: 30.00")
        
        # Get premium search terms
        search_terms = self.get_enhanced_search_terms(category)
        all_candidates = set()
        
        print(f"📋 Using {len(search_terms)} premium search strategies")
        
        # Execute searches quickly
        for i, term in enumerate(search_terms, 1):
            print(f"🔍 Search {i}: {term[:50]}...")
            
            query = SearchQuery(
                query_text=term,
                job_category=category,
                strategy=SearchStrategy.HYBRID,
                max_candidates=300  # Increased for better coverage
            )
            
            try:
                candidates = self.search_agent.search_service.search_candidates(
                    query, SearchStrategy.HYBRID
                )
                
                for candidate in candidates:
                    all_candidates.add(candidate.id)
                
                print(f"   Found: {len(candidates)} | Total unique: {len(all_candidates)}")
                
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
                continue
        
        if len(all_candidates) < 10:
            print(f"   ⚠️ Only {len(all_candidates)} candidates found (need 10)")
            return None
        
        # Take top 10 candidates
        candidate_ids = list(all_candidates)[:10]
        print(f"✅ Selected {len(candidate_ids)} candidates")
        
        # Quick evaluation (no delays)
        print(f"📊 Evaluating {category}...")
        try:
            result = self.evaluation_service.evaluate_candidates(category, candidate_ids)
            
            if result and hasattr(result, 'average_final_score'):
                new_score = result.average_final_score
                improvement = new_score - target_info['current']
                
                print(f"🎉 RESULT: {new_score:.2f} (change: {improvement:+.2f})")
                
                if new_score >= 30.0:
                    print(f"🏆 SUCCESS! {category} reached target!")
                    return {"category": category, "score": new_score, "success": True}
                else:
                    return {"category": category, "score": new_score, "success": False}
            else:
                print(f"❌ Evaluation failed")
                return None
                
        except Exception as e:
            print(f"❌ Evaluation error: {e}")
            return None
    
    def run_fast_improvement(self):
        """Run fast improvement for all categories."""
        print("🚀 FAST IMPROVEMENT - NO RATE LIMITS")
        print("=" * 60)
        
        results = []
        successes = 0
        
        # Sort by deficit (easiest first)
        sorted_categories = sorted(
            TARGET_CATEGORIES.items(), 
            key=lambda x: x[1]['deficit']
        )
        
        for category, target_info in sorted_categories:
            print(f"\n🎯 TARGETING: {category}")
            
            for attempt in range(1, self.max_attempts + 1):
                print(f"\n📍 ATTEMPT {attempt}/{self.max_attempts}")
                
                result = self.fast_search_and_evaluate(category, target_info)
                
                if result:
                    results.append(result)
                    if result['success']:
                        successes += 1
                        print(f"🎊 {category} COMPLETED!")
                        break
                    else:
                        # Update for next attempt
                        target_info['current'] = result['score']
                        target_info['deficit'] = 30.0 - result['score']
                        print(f"🔄 Updated: {target_info['current']:.2f} (gap: -{target_info['deficit']:.2f})")
                
                # Minimal delay between attempts (5 seconds)
                if attempt < self.max_attempts:
                    print("⏱️ Quick pause...")
                    time.sleep(5)
            
            # Small delay between categories (10 seconds)
            print("⏱️ Moving to next category...")
            time.sleep(10)
        
        # Final summary
        print("\n" + "=" * 60)
        print("🏁 FAST IMPROVEMENT RESULTS")
        print("=" * 60)
        
        for result in results:
            status = "✅ SUCCESS" if result['success'] else "📈 IMPROVED"
            print(f"{status} {result['category']}: {result['score']:.2f}")
        
        print(f"\n🎯 SUCCESS RATE: {successes}/{len(TARGET_CATEGORIES)}")
        
        if successes == 3:
            print("🎉 ALL CATEGORIES ABOVE 30! MISSION COMPLETE!")
        else:
            remaining = 3 - successes
            print(f"🔄 {remaining} categories still need work")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"results/fast_improvement_{timestamp}.json"
        
        summary = {
            "timestamp": timestamp,
            "approach": "fast_no_rate_limits",
            "target_categories": TARGET_CATEGORIES,
            "results": results,
            "successes": successes,
            "total_categories": len(TARGET_CATEGORIES)
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"💾 Results saved: {results_file}")
        
        return results

def main():
    """Main execution."""
    try:
        improver = FastImprover()
        results = improver.run_fast_improvement()
        
        # Quick status check
        print("\n🔍 QUICK STATUS:")
        for result in results:
            gap = 30.0 - result['score'] if result['score'] < 30.0 else 0
            print(f"   {result['category']}: {result['score']:.2f} (gap: -{gap:.2f})")
            
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 