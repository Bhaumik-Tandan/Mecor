#!/usr/bin/env python3
"""
🎯 FOCUSED CONTINUOUS OPTIMIZER
==============================
Aggressive optimization for the 3 categories below 30.
Runs continuously until ALL are above 30, then submits.
"""

import json
import os
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List

# Import our modules
from src.main import SearchAgent
from src.agents.validation_agent import IntelligentValidationAgent
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy

class FocusedOptimizer:
    def __init__(self):
        print("🎯 INITIALIZING FOCUSED CONTINUOUS OPTIMIZER")
        
        # Target categories that need work (below 30)
        self.target_categories = {
            "doctors_md.yml": 16.0,        # needs +14
            "anthropology.yml": 17.33,     # needs +12.67
            "quantitative_finance.yml": 17.33  # needs +12.67
        }
        
        self.target_score = 30.0
        self.search_agent = SearchAgent()
        self.search_service = SearchService()
        self.intelligent_validator = IntelligentValidationAgent()
        
        # Aggressive settings for faster optimization
        self.base_delay = 30  # Shorter delays
        self.max_attempts_per_category = 10  # More attempts
        
        self.start_time = datetime.now()
        self.iteration = 0
        
        # Prevent sleep
        self.prevent_sleep()
        
        print(f"✅ Optimizer initialized for {len(self.target_categories)} categories")
        print(f"🎯 Target: Get all above {self.target_score}")
        
    def prevent_sleep(self):
        """Prevent computer from sleeping"""
        try:
            subprocess.run(['pkill', '-f', 'caffeinate'], capture_output=True)
            self.caffeinate_process = subprocess.Popen(
                ['caffeinate', '-d', '-i', '-m', '-s'], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            print("☕ Sleep prevention activated")
        except Exception as e:
            print(f"⚠️ Sleep prevention failed: {e}")
    
    def get_current_scores(self) -> Dict[str, float]:
        """Get current scores for target categories"""
        try:
            print("📊 Getting current scores...")
            result = self.search_agent.run_evaluation()
            
            if result and 'scores' in result:
                scores = {}
                for category in self.target_categories.keys():
                    if category in result['scores']:
                        scores[category] = float(result['scores'][category])
                        
                print(f"✅ Current scores: {scores}")
                return scores
            else:
                print("❌ Failed to get scores")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting scores: {e}")
            return {}
    
    def optimize_category(self, category: str, current_score: float) -> bool:
        """Aggressively optimize a single category"""
        print(f"\n🔥 OPTIMIZING {category} (current: {current_score:.2f})")
        
        # Multiple optimization strategies
        strategies = [
            "enhanced search terms",
            "specialized queries", 
            "industry-specific keywords",
            "skill-based search",
            "experience-focused search"
        ]
        
        for attempt, strategy in enumerate(strategies, 1):
            try:
                print(f"🔄 Attempt {attempt}: {strategy}")
                
                # Create specialized search query
                search_term = self.generate_search_term(category, strategy)
                print(f"🔍 Search term: {search_term}")
                
                # Run intelligent search
                search_query = SearchQuery(
                    query_text=search_term,
                    job_category=category,
                    strategy=SearchStrategy.HYBRID,
                    max_candidates=50
                )
                
                result = self.intelligent_validator.orchestrate_search(search_query)
                
                if result:
                    print(f"✅ Optimization attempt completed")
                    time.sleep(self.base_delay)  # Shorter delay
                    return True
                else:
                    print(f"⚠️ Optimization attempt {attempt} had issues")
                    
            except Exception as e:
                print(f"❌ Optimization attempt {attempt} failed: {e}")
                
            time.sleep(15)  # Quick delay between attempts
            
        return False
    
    def generate_search_term(self, category: str, strategy: str) -> str:
        """Generate specialized search terms based on category and strategy"""
        
        category_terms = {
            "doctors_md.yml": {
                "enhanced search terms": "experienced primary care physician family medicine MD",
                "specialized queries": "board certified family doctor general practitioner",
                "industry-specific keywords": "clinical experience outpatient care medical doctor",
                "skill-based search": "patient care diagnosis treatment family medicine",
                "experience-focused search": "3+ years clinical practice MD degree family medicine"
            },
            "anthropology.yml": {
                "enhanced search terms": "PhD anthropology ethnographic research cultural studies",
                "specialized queries": "social anthropology qualitative research field work",
                "industry-specific keywords": "ethnography applied anthropology research methods",
                "skill-based search": "qualitative analysis cultural research anthropological methods",
                "experience-focused search": "recent PhD anthropology dissertation research"
            },
            "quantitative_finance.yml": {
                "enhanced search terms": "quantitative analyst financial modeling derivatives",
                "specialized queries": "quantitative finance risk management trading algorithms",
                "industry-specific keywords": "financial engineering quantitative research portfolio",
                "skill-based search": "Python quantitative analysis financial mathematics",
                "experience-focused search": "3+ years quantitative finance MBA experience"
            }
        }
        
        return category_terms.get(category, {}).get(strategy, category.replace("_", " ").replace(".yml", ""))
    
    def get_category_candidates(self, category: str) -> List[str]:
        """Get candidates for final submission"""
        try:
            all_candidates = set()
            strategies = [SearchStrategy.HYBRID, SearchStrategy.VECTOR_ONLY, SearchStrategy.BM25_ONLY]
            
            for strategy in strategies:
                query = SearchQuery(
                    query_text=category.replace("_", " ").replace(".yml", ""),
                    job_category=category,
                    strategy=strategy,
                    max_candidates=30
                )
                
                candidates = self.search_service.search_candidates(query, strategy)
                if candidates:
                    candidate_ids = [c.id for c in candidates[:25]]
                    all_candidates.update(candidate_ids)
                    
                time.sleep(5)
                
            return list(all_candidates)[:10]
            
        except Exception as e:
            print(f"❌ Error getting candidates for {category}: {e}")
            return []
    
    def submit_to_grade_api(self) -> bool:
        """Submit all categories to grade API when ready"""
        try:
            print("🚀 PREPARING FINAL SUBMISSION TO GRADE API...")
            
            # Get all 10 categories for complete submission
            all_categories = [
                "junior_corporate_lawyer.yml", "tax_lawyer.yml", "biology_expert.yml",
                "radiology.yml", "mathematics_phd.yml", "bankers.yml", 
                "mechanical_engineers.yml", "doctors_md.yml", 
                "anthropology.yml", "quantitative_finance.yml"
            ]
            
            all_candidates = {}
            
            for category in all_categories:
                print(f"🔍 Getting candidates for {category}")
                candidates = self.get_category_candidates(category)
                all_candidates[category] = candidates
                print(f"✅ Got {len(candidates)} candidates for {category}")
            
            # Submit to grade API
            payload = {"config_candidates": all_candidates}
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'bhaumik.tandan@gmail.com'
            }
            
            response = requests.post(
                'https://mercor-dev--search-eng-interview.modal.run/grade',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            print(f"📡 Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                print("🎊 SUCCESS! ALL CATEGORIES SUBMITTED TO GRADE API!")
                return True
            else:
                print(f"❌ Submission failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Submission error: {e}")
            return False
    
    def run_continuous_optimization(self):
        """Main continuous optimization loop"""
        print("\n🎯 STARTING CONTINUOUS OPTIMIZATION")
        print("=" * 60)
        print(f"🎯 Target: Get all 3 categories above {self.target_score}")
        print(f"📊 Categories to optimize: {list(self.target_categories.keys())}")
        print()
        
        while True:
            self.iteration += 1
            runtime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            
            print(f"\n🔄 ITERATION {self.iteration} (Runtime: {runtime_hours:.1f}h)")
            print("=" * 50)
            
            # Get current scores
            current_scores = self.get_current_scores()
            
            if not current_scores:
                print("⚠️ Could not get scores, retrying...")
                time.sleep(60)
                continue
            
            # Check which categories still need work
            categories_below_30 = []
            categories_ready = []
            
            for category, score in current_scores.items():
                if score < self.target_score:
                    categories_below_30.append((category, score))
                else:
                    categories_ready.append((category, score))
            
            print(f"\n📊 STATUS:")
            print(f"✅ Ready (30+): {len(categories_ready)}")
            print(f"❌ Below 30: {len(categories_below_30)}")
            
            # If all are ready, submit and finish!
            if len(categories_below_30) == 0:
                print("\n🎊 ALL CATEGORIES ABOVE 30! SUBMITTING TO GRADE API!")
                
                if self.submit_to_grade_api():
                    print("🎊 MISSION ACCOMPLISHED! ALL CATEGORIES SUBMITTED!")
                    break
                else:
                    print("❌ Submission failed, but all categories are optimized")
                    break
            
            # Optimize categories that need work
            for category, score in categories_below_30:
                points_needed = self.target_score - score
                print(f"\n🎯 {category}: {score:.2f} (needs +{points_needed:.2f})")
                
                self.optimize_category(category, score)
            
            # Show progress
            print(f"\n📈 PROGRESS:")
            for category, score in current_scores.items():
                status = "✅" if score >= self.target_score else "❌"
                print(f"   {status} {category}: {score:.2f}")
            
            print(f"\n⏱️ Waiting {self.base_delay}s before next iteration...")
            time.sleep(self.base_delay)

if __name__ == "__main__":
    optimizer = FocusedOptimizer()
    try:
        optimizer.run_continuous_optimization()
    except KeyboardInterrupt:
        print("\n⏸️ Optimization stopped by user")
    finally:
        # Clean up
        if hasattr(optimizer, 'caffeinate_process'):
            try:
                optimizer.caffeinate_process.terminate()
            except:
                pass 