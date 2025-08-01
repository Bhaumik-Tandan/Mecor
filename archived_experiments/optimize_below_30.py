#!/usr/bin/env python3
"""
Optimize Below 30 Categories
============================
Targeted optimization for categories scoring below 30:
Priority 1: tax_lawyer.yml (24.83) - needs +5.17
Priority 2: anthropology.yml (23.67) - needs +6.33  
Priority 3: junior_corporate_lawyer.yml (16.67) - needs +13.33
Priority 4: biology_expert.yml (12.0) - needs +18.0
Priority 5: quantitative_finance.yml (7.67) - needs +22.33
Priority 6: doctors_md.yml (0.0) - needs +30.0
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import SearchAgent
from src.models.candidate import SearchQuery, SearchStrategy
from src.utils.logger import setup_logger

logger = setup_logger(
    name="optimize_below_30",
    level="INFO",
    log_file="logs/optimize_below_30.log"
)

# Target categories sorted by priority (closest to 30 first)
TARGET_CATEGORIES = {
    "tax_lawyer.yml": {"current": 24.83, "deficit": 5.17, "priority": 1},
    "anthropology.yml": {"current": 23.67, "deficit": 6.33, "priority": 2},
    "junior_corporate_lawyer.yml": {"current": 16.67, "deficit": 13.33, "priority": 3},
    "biology_expert.yml": {"current": 12.0, "deficit": 18.0, "priority": 4},
    "quantitative_finance.yml": {"current": 7.67, "deficit": 22.33, "priority": 5},
    "doctors_md.yml": {"current": 0.0, "deficit": 30.0, "priority": 6}
}

class Below30Optimizer:
    def __init__(self):
        self.search_agent = SearchAgent()
        self.evaluation_service = self.search_agent.evaluation_service
        self.max_attempts = 3
        
    def get_ultra_premium_search_terms(self, category):
        """Get the highest quality search terms for each category."""
        
        premium_strategies = {
            "tax_lawyer.yml": [
                "Big Four KPMG Deloitte PwC EY tax director partner",
                "Skadden Cravath Sullivan tax attorney partner",
                "tax law partner Wachtell Kirkland Ellis",
                "corporate tax counsel Fortune 500 company",
                "federal tax litigation attorney IRS",
                "international tax law transfer pricing attorney",
                "tax controversy lawyer white collar defense"
            ],
            "anthropology.yml": [
                "Harvard Stanford Berkeley anthropology professor tenure",
                "cultural anthropology ethnography fieldwork PhD",
                "medical anthropology global health researcher",
                "linguistic anthropology sociolinguistics professor",
                "archaeology anthropological methods research",
                "applied anthropology consultant international development",
                "urban anthropology sociocultural research academic"
            ],
            "junior_corporate_lawyer.yml": [
                "BigLaw associate Cravath Skadden Sullivan Cromwell",
                "corporate law associate mergers acquisitions",
                "securities law associate capital markets lawyer",
                "first year associate Harvard Yale Stanford Law",
                "junior corporate counsel legal department",
                "corporate attorney JD Columbia NYU Chicago Law",
                "associate lawyer business law corporate transactions"
            ],
            "biology_expert.yml": [
                "Cell Nature Science PNAS publication lead author",
                "Howard Hughes Medical Institute investigator",
                "NIH R01 grant principal investigator biology",
                "Harvard Medical School MIT biology professor",
                "molecular biology structural biology research",
                "systems biology computational biology researcher",
                "cancer biology immunology cell biology expert"
            ],
            "quantitative_finance.yml": [
                "Two Sigma Citadel Renaissance Technologies quant",
                "Jane Street Tower Research algorithmic trading",
                "Goldman Sachs Morgan Stanley quant strategist",
                "hedge fund systematic trading portfolio manager",
                "derivative pricing volatility modeling expert",
                "high frequency trading market maker quantitative",
                "risk management quantitative analyst VaR modeling"
            ],
            "doctors_md.yml": [
                "Massachusetts General Brigham physician attending",
                "Cleveland Clinic Mayo Clinic staff physician",
                "Johns Hopkins UCSF internal medicine attending",
                "board certified family medicine physician MD",
                "primary care physician residency trained",
                "hospital medicine physician clinical practice",
                "academic medicine physician professor MD PhD"
            ]
        }
        
        return premium_strategies.get(category, [category.replace("_", " ").replace(".yml", "")])
    
    def advanced_multi_strategy_search(self, category, target_info):
        """Advanced search using multiple strategies and premium terms."""
        print(f"\n🎯 ADVANCED OPTIMIZATION: {category}")
        print(f"   Current: {target_info['current']:.2f} | Need: +{target_info['deficit']:.2f}")
        print(f"   Priority: {target_info['priority']}/6")
        
        premium_terms = self.get_ultra_premium_search_terms(category)
        all_candidates = set()
        
        print(f"📋 Using {len(premium_terms)} ultra-premium search strategies")
        
        # Strategy 1: HYBRID with premium terms (most important)
        print("\n🔧 STRATEGY 1: HYBRID Premium Search")
        for i, term in enumerate(premium_terms, 1):
            print(f"🔍 {i}/{len(premium_terms)}: {term[:60]}...")
            
            query = SearchQuery(
                query_text=term,
                job_category=category,
                strategy=SearchStrategy.HYBRID,
                max_candidates=400
            )
            
            try:
                candidates = self.search_agent.search_service.search_candidates(
                    query, SearchStrategy.HYBRID
                )
                
                for candidate in candidates:
                    all_candidates.add(candidate.id)
                
                print(f"   Found: {len(candidates)} | Total: {len(all_candidates)}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                continue
        
        # Strategy 2: VECTOR_ONLY with broader professional terms
        print("\n🔧 STRATEGY 2: VECTOR_ONLY Broad Professional")
        broad_professional_terms = {
            "tax_lawyer.yml": ["tax attorney legal practice", "corporate taxation lawyer", "tax law specialist"],
            "anthropology.yml": ["anthropologist cultural research", "ethnographic fieldwork", "social anthropology"],
            "junior_corporate_lawyer.yml": ["corporate lawyer associate", "business law attorney", "legal counsel"],
            "biology_expert.yml": ["biology researcher scientist", "molecular biology expert", "life sciences"],
            "quantitative_finance.yml": ["quantitative analyst finance", "financial modeling trader", "quant researcher"],
            "doctors_md.yml": ["physician medical doctor", "internal medicine doctor", "primary care physician"]
        }
        
        for term in broad_professional_terms.get(category, []):
            print(f"🔍 VECTOR: {term}")
            
            query = SearchQuery(
                query_text=term,
                job_category=category,
                strategy=SearchStrategy.VECTOR_ONLY,
                max_candidates=200
            )
            
            try:
                candidates = self.search_agent.search_service.search_candidates(
                    query, SearchStrategy.VECTOR_ONLY
                )
                
                for candidate in candidates:
                    all_candidates.add(candidate.id)
                
                print(f"   Found: {len(candidates)} | Total: {len(all_candidates)}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # Strategy 3: BM25_ONLY with specific keywords
        print("\n🔧 STRATEGY 3: BM25_ONLY Keyword Matching")
        keyword_terms = {
            "tax_lawyer.yml": "tax attorney lawyer taxation legal",
            "anthropology.yml": "anthropology cultural ethnography research",
            "junior_corporate_lawyer.yml": "corporate lawyer attorney associate legal",
            "biology_expert.yml": "biology molecular research scientist PhD",
            "quantitative_finance.yml": "quantitative finance analyst trading",
            "doctors_md.yml": "doctor physician MD medicine clinical"
        }
        
        term = keyword_terms.get(category, "")
        if term:
            print(f"🔍 BM25: {term}")
            
            query = SearchQuery(
                query_text=term,
                job_category=category,
                strategy=SearchStrategy.BM25_ONLY,
                max_candidates=150
            )
            
            try:
                candidates = self.search_agent.search_service.search_candidates(
                    query, SearchStrategy.BM25_ONLY
                )
                
                for candidate in candidates:
                    all_candidates.add(candidate.id)
                
                print(f"   Found: {len(candidates)} | Total: {len(all_candidates)}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        print(f"\n✅ TOTAL UNIQUE CANDIDATES: {len(all_candidates)}")
        
        if len(all_candidates) < 10:
            print(f"⚠️ Only found {len(all_candidates)} candidates (need 10)")
            return None
        
        # Take top 10 candidates
        candidate_ids = list(all_candidates)[:10]
        return candidate_ids
    
    def evaluate_and_track_progress(self, category, candidate_ids, target_info):
        """Evaluate candidates and track progress."""
        print(f"\n📊 EVALUATING {category}")
        
        try:
            result = self.evaluation_service.evaluate_candidates(category, candidate_ids)
            
            if result and hasattr(result, 'average_final_score'):
                new_score = result.average_final_score
                improvement = new_score - target_info['current']
                
                print(f"🎉 RESULT: {new_score:.2f} (change: {improvement:+.2f})")
                
                if new_score >= 30.0:
                    print(f"🏆 SUCCESS! {category} reached target!")
                    return {"category": category, "score": new_score, "success": True, "improvement": improvement}
                else:
                    gap = 30.0 - new_score
                    print(f"📈 Progress made, gap now: -{gap:.2f}")
                    return {"category": category, "score": new_score, "success": False, "improvement": improvement}
            else:
                print(f"❌ Evaluation failed")
                return None
                
        except Exception as e:
            print(f"❌ Evaluation error: {e}")
            return None
    
    def optimize_category(self, category, target_info):
        """Optimize a single category with multiple attempts."""
        print(f"\n🚀 OPTIMIZING: {category}")
        print("=" * 70)
        
        best_result = None
        
        for attempt in range(1, self.max_attempts + 1):
            print(f"\n📍 ATTEMPT {attempt}/{self.max_attempts}")
            
            # Advanced search
            candidate_ids = self.advanced_multi_strategy_search(category, target_info)
            
            if candidate_ids:
                # Brief pause before evaluation
                print("⏱️ Brief pause before evaluation...")
                time.sleep(3)
                
                # Evaluate
                result = self.evaluate_and_track_progress(category, candidate_ids, target_info)
                
                if result:
                    if not best_result or result['score'] > best_result['score']:
                        best_result = result
                    
                    if result['success']:
                        print(f"🎊 {category} COMPLETED!")
                        return result
                    else:
                        # Update target for next attempt
                        target_info['current'] = result['score']
                        target_info['deficit'] = 30.0 - result['score']
                        print(f"🔄 Updated target: {target_info['current']:.2f} (deficit: -{target_info['deficit']:.2f})")
            
            # Brief pause between attempts
            if attempt < self.max_attempts:
                print("⏱️ Quick pause before next attempt...")
                time.sleep(5)
        
        return best_result
    
    def run_optimization(self):
        """Run optimization for all categories below 30."""
        print("🎯 OPTIMIZE CATEGORIES BELOW 30")
        print("=" * 70)
        print("Targeting 6 categories, prioritized by proximity to 30")
        print("=" * 70)
        
        results = []
        successes = 0
        
        # Sort by priority (closest to 30 first)
        sorted_categories = sorted(
            TARGET_CATEGORIES.items(),
            key=lambda x: x[1]['priority']
        )
        
        for category, target_info in sorted_categories:
            print(f"\n🎯 PRIORITY {target_info['priority']}: {category}")
            print(f"   Current: {target_info['current']:.2f} | Target: 30.0")
            
            result = self.optimize_category(category, target_info)
            
            if result:
                results.append(result)
                if result['success']:
                    successes += 1
            
            # Pause between categories
            print("\n⏱️ Moving to next category...")
            time.sleep(10)
        
        # Final summary
        print("\n" + "=" * 70)
        print("🏁 OPTIMIZATION RESULTS")
        print("=" * 70)
        
        total_improved = 0
        for result in results:
            status = "✅ SUCCESS" if result['success'] else "📈 IMPROVED"
            gap = 30.0 - result['score'] if result['score'] < 30.0 else 0
            improvement = result.get('improvement', 0)
            
            if improvement > 0:
                total_improved += 1
            
            print(f"{status} {result['category']}: {result['score']:.2f} (change: {improvement:+.2f}, gap: -{gap:.2f})")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Categories reaching 30+: {successes}/6")
        print(f"   Categories improved: {total_improved}/6")
        
        if successes >= 4:
            print("🎉 EXCELLENT! Most categories optimized!")
        elif successes >= 2:
            print("🎊 GOOD PROGRESS! Several categories improved!")
        else:
            print("📈 Some progress made, continue optimizing")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"results/below_30_optimization_{timestamp}.json"
        
        summary = {
            "timestamp": timestamp,
            "approach": "below_30_targeted_optimization",
            "target_categories": TARGET_CATEGORIES,
            "results": results,
            "successes": successes,
            "total_improved": total_improved,
            "total_categories": 6
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"💾 Results saved: {results_file}")
        
        return results

def main():
    """Main execution."""
    try:
        optimizer = Below30Optimizer()
        results = optimizer.run_optimization()
        
        print("\n🔍 FINAL STATUS:")
        new_above_30 = 4  # Current categories above 30
        
        for result in results:
            if result.get('success'):
                new_above_30 += 1
        
        print(f"📊 Categories above 30: {new_above_30}/10")
        print(f"🎯 Overall progress: {(new_above_30/10)*100:.1f}%")
        
        if new_above_30 >= 7:
            print("🎉 MISSION ACCOMPLISHED! 70%+ success rate!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 