#!/usr/bin/env python3
"""
🎯 FINAL TARGETED OPTIMIZER
===========================
Focused optimization for the 4 categories below 30.
Uses the proven score extraction method.
"""

import json
import os
import time
import requests
import subprocess
import sys
from datetime import datetime
from typing import Dict, List
from improved_score_extractor import ImprovedScoreExtractor
from src.agents.validation_agent import IntelligentValidationAgent
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy
from src.config.settings import config

class FinalTargetedOptimizer:
    def __init__(self):
        # Target categories that need improvement
        self.target_categories = {
            "doctors_md.yml": 16.00,
            "anthropology.yml": 17.33,
            "quantitative_finance.yml": 17.33,
            "tax_lawyer.yml": 29.33
        }
        
        # Ready categories (above 30)
        self.ready_categories = {
            "junior_corporate_lawyer.yml": 77.33,
            "biology_expert.yml": 32.00,
            "radiology.yml": 30.33,
            "mathematics_phd.yml": 51.00,
            "bankers.yml": 68.00,
            "mechanical_engineers.yml": 69.00
        }
        
        self.target_score = 30.0
        self.score_extractor = ImprovedScoreExtractor()
        self.search_service = SearchService()
        self.intelligent_validator = IntelligentValidationAgent()
        self.max_attempts_per_category = 15
        self.base_delay = 45  # Conservative delays
        self.start_time = datetime.now()
        self.iteration = 0
        
        # Prevent sleep
        self.prevent_sleep()
        
        print("🎯 FINAL TARGETED OPTIMIZER INITIALIZED")
        print(f"📋 Target categories: {len(self.target_categories)}")
        print(f"✅ Ready categories: {len(self.ready_categories)}")
        print(f"🎯 Target score: {self.target_score}")
        
    def prevent_sleep(self):
        """Prevent computer from sleeping"""
        try:
            subprocess.Popen(['caffeinate', '-d'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("☕ Sleep prevention activated")
        except:
            print("⚠️ Could not activate sleep prevention")
    
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"{timestamp} | {message}"
        print(log_message)
        
        # Also save to file
        with open("final_optimizer.log", "a") as f:
            f.write(log_message + "\n")
    
    def get_current_scores(self) -> Dict[str, float]:
        """Get current scores using proven extraction method"""
        try:
            scores = self.score_extractor.extract_scores_robust()
            if scores:
                self.log(f"✅ Successfully extracted {len(scores)} scores")
                return scores
            else:
                self.log("❌ Failed to extract scores")
                return {}
        except Exception as e:
            self.log(f"❌ Score extraction error: {e}")
            return {}
    
    def optimize_category(self, category: str) -> bool:
        """Optimize a specific category"""
        self.log(f"🎯 Optimizing {category}...")
        
        try:
            # Generate enhanced search terms
            search_terms = self.generate_enhanced_search_terms(category)
            
            for attempt, search_term in enumerate(search_terms[:3], 1):
                self.log(f"📝 Attempt {attempt}: {search_term}")
                
                # Use intelligent validator for optimization
                query = SearchQuery(
                    query_text=search_term,
                    job_category=category,
                    strategy=SearchStrategy.HYBRID
                )
                
                suggestions = self.intelligent_validator.validate_and_suggest_improvements(
                    query, self.search_service
                )
                
                self.log(f"💡 Applied {len(suggestions)} improvements")
                
                # Small delay between attempts
                time.sleep(self.base_delay)
                
            return True
            
        except Exception as e:
            self.log(f"❌ Error optimizing {category}: {e}")
            return False
    
    def generate_enhanced_search_terms(self, category: str) -> List[str]:
        """Generate enhanced search terms for specific categories"""
        base_terms = {
            "doctors_md.yml": [
                "family medicine physician electronic health records telemedicine",
                "primary care doctor EHR systems virtual consultations",
                "general practitioner EMR telemedicine platform experience"
            ],
            "anthropology.yml": [
                "social anthropologist ethnographic fieldwork research methods",
                "cultural anthropology applied research policy analysis",
                "anthropological research community engagement social systems"
            ],
            "quantitative_finance.yml": [
                "quantitative analyst Python financial modeling derivatives",
                "quant researcher algorithmic trading risk management",
                "financial engineer mathematical modeling portfolio optimization"
            ],
            "tax_lawyer.yml": [
                "tax attorney corporate transactions IRS audit defense",
                "tax lawyer business law legal writing expertise",
                "corporate tax counsel transaction advisory services"
            ]
        }
        
        return base_terms.get(category, ["advanced professional experience"])
    
    def check_completion(self) -> bool:
        """Check if all categories are above 30"""
        scores = self.get_current_scores()
        if not scores:
            return False
            
        below_30 = {k: v for k, v in scores.items() if v < 30.0}
        
        if not below_30:
            self.log("🎉 ALL CATEGORIES ABOVE 30! OPTIMIZATION COMPLETE!")
            return True
        
        self.log(f"📊 Still need work: {len(below_30)} categories")
        for cat, score in below_30.items():
            self.log(f"   • {cat}: {score:.2f}")
        
        return False
    
    def submit_all_to_grade_api(self):
        """Submit all 10 categories to grade API"""
        self.log("🎊 SUBMITTING ALL CATEGORIES TO GRADE API...")
        
        try:
            # Get candidates for all categories
            all_categories = list(self.target_categories.keys()) + list(self.ready_categories.keys())
            config_candidates = {}
            
            for category in all_categories:
                self.log(f"📋 Collecting candidates for {category}...")
                candidates = self.get_category_candidates(category)
                if candidates:
                    config_candidates[category.replace('.yml', '')] = candidates
                else:
                    self.log(f"❌ No candidates for {category}")
            
            # Submit to grade API
            if len(config_candidates) == 10:
                response = requests.post(
                    "https://mercor-dev--search-eng-interview.modal.run/grade",
                    json={"config_candidates": config_candidates},
                    headers={"Authorization": config.USER_EMAIL},
                    timeout=120
                )
                
                self.log(f"📤 Grade API Response: {response.status_code}")
                self.log(f"📝 Response: {response.text}")
                
                if response.status_code == 200:
                    self.log("🎉 SUCCESSFULLY SUBMITTED TO GRADE API!")
                    return True
                else:
                    self.log(f"❌ Grade API failed: {response.text}")
                    return False
            else:
                self.log(f"❌ Missing categories. Got {len(config_candidates)}, need 10")
                return False
                
        except Exception as e:
            self.log(f"❌ Grade API submission error: {e}")
            return False
    
    def get_category_candidates(self, category: str) -> List[dict]:
        """Get top 10 candidates for a category"""
        try:
            query = SearchQuery(
                query_text="professional experienced qualified",
                job_category=category,
                strategy=SearchStrategy.HYBRID
            )
            
            candidates = self.search_service.search_candidates(query)
            
            # Return top 10 candidates with required format
            top_candidates = []
            for candidate in candidates[:10]:
                top_candidates.append({
                    "candidate_name": candidate.get("name", ""),
                    "candidate_linkedin_url": f"https://www.linkedin.com/in/{candidate.get('linkedinId', '')}",
                    "raw_data": candidate
                })
            
            return top_candidates
            
        except Exception as e:
            self.log(f"❌ Error getting candidates for {category}: {e}")
            return []
    
    def run_optimization(self):
        """Run the complete optimization process"""
        self.log("🚀 STARTING FINAL TARGETED OPTIMIZATION")
        
        while True:
            self.iteration += 1
            self.log(f"\n🔄 ITERATION {self.iteration}")
            
            # Check current status
            if self.check_completion():
                # All categories above 30 - submit to grade API
                if self.submit_all_to_grade_api():
                    self.log("✅ MISSION ACCOMPLISHED!")
                    break
                else:
                    self.log("❌ Submission failed, but optimization complete")
                    break
            
            # Optimize each target category
            for category in self.target_categories.keys():
                if self.iteration <= self.max_attempts_per_category:
                    self.optimize_category(category)
                    time.sleep(30)  # Delay between categories
            
            # Check progress after each round
            self.log(f"⏱️ Iteration {self.iteration} complete. Checking progress...")
            time.sleep(60)  # Wait before next iteration
            
            if self.iteration >= self.max_attempts_per_category:
                self.log("⚠️ Maximum attempts reached. Checking final status...")
                break
        
        self.log("🏁 FINAL TARGETED OPTIMIZER COMPLETE")

if __name__ == "__main__":
    optimizer = FinalTargetedOptimizer()
    optimizer.run_optimization() 