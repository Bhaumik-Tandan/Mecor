#!/usr/bin/env python3
"""
🌙 AGGRESSIVE NIGHT OPTIMIZER
=============================
Overnight optimization for the 4 categories below 30.
Multiple strategies, high iteration count, smart delays.
"""

import json
import os
import time
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List
from improved_score_extractor import ImprovedScoreExtractor
from src.agents.validation_agent import IntelligentValidationAgent
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy
from src.config.settings import config

class AggressiveNightOptimizer:
    def __init__(self):
        # Target categories below 30
        self.target_categories = {
            "doctors_md.yml": 16.00,
            "anthropology.yml": 17.33,
            "quantitative_finance.yml": 17.33,
            "tax_lawyer.yml": 29.33  # Close to 30!
        }
        
        # Current good categories (above 30)
        self.good_categories = {
            "junior_corporate_lawyer.yml": 77.33,
            "biology_expert.yml": 32.00,
            "radiology.yml": 30.33,
            "mathematics_phd.yml": 51.00,
            "bankers.yml": 85.33,
            "mechanical_engineers.yml": 69.00
        }
        
        self.target_score = 30.0
        self.score_extractor = ImprovedScoreExtractor()
        self.search_service = SearchService()
        self.intelligent_validator = IntelligentValidationAgent()
        
        # Aggressive settings for overnight run
        self.max_iterations = 50  # High iteration count
        self.strategies_per_category = 5  # Multiple strategies per category
        self.base_delay = 30  # Shorter delays for more attempts
        self.evaluation_interval = 5  # Check scores every 5 iterations
        
        self.start_time = datetime.now()
        self.iteration = 0
        self.last_scores = {}
        
        # Prevent sleep and setup logging
        self.prevent_sleep()
        self.setup_logging()
        
        print("🌙 AGGRESSIVE NIGHT OPTIMIZER INITIALIZED")
        print(f"🎯 Target categories: {len(self.target_categories)}")
        print(f"⏰ Max iterations: {self.max_iterations}")
        print(f"🚀 Deadline: 11 PM PST (14+ hours)")
        
    def prevent_sleep(self):
        """Prevent computer from sleeping"""
        try:
            subprocess.Popen(['caffeinate', '-d'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("☕ Sleep prevention activated")
        except:
            print("⚠️ Could not activate sleep prevention")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        self.log_file = "night_optimizer.log"
        self.progress_file = "night_progress.json"
        
        # Clear previous logs
        with open(self.log_file, "w") as f:
            f.write(f"🌙 NIGHT OPTIMIZER STARTED: {datetime.now()}\n")
    
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"{timestamp} | {message}"
        print(log_message)
        
        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")
    
    def save_progress(self, scores: Dict[str, float]):
        """Save current progress"""
        progress = {
            "timestamp": datetime.now().isoformat(),
            "iteration": self.iteration,
            "runtime_minutes": (datetime.now() - self.start_time).total_seconds() / 60,
            "current_scores": scores,
            "target_categories": self.target_categories,
            "categories_above_30": len([s for s in scores.values() if s >= 30]),
            "total_categories": len(scores)
        }
        
        with open(self.progress_file, "w") as f:
            json.dump(progress, f, indent=2)
    
    def get_current_scores(self) -> Dict[str, float]:
        """Get current scores"""
        try:
            scores = self.score_extractor.extract_scores_robust()
            if scores:
                self.log(f"✅ Successfully extracted {len(scores)} scores")
                self.save_progress(scores)
                return scores
            else:
                self.log("❌ Failed to extract scores")
                return self.last_scores
        except Exception as e:
            self.log(f"❌ Score extraction error: {e}")
            return self.last_scores
    
    def generate_advanced_search_terms(self, category: str, strategy_num: int) -> List[str]:
        """Generate multiple advanced search strategies per category"""
        
        strategies = {
            "doctors_md.yml": [
                # Strategy 1: EHR focus
                ["family medicine physician electronic health records", "primary care doctor EHR systems", "general practitioner EMR experience"],
                # Strategy 2: Telemedicine focus  
                ["telemedicine physician virtual consultations", "remote healthcare doctor telehealth", "digital health primary care"],
                # Strategy 3: US medical education focus
                ["US medical school graduate family medicine", "American trained physician primary care", "USMLE family medicine doctor"],
                # Strategy 4: Hospital experience focus
                ["hospital physician family medicine", "inpatient outpatient family doctor", "clinical experience primary care"],
                # Strategy 5: Board certification focus
                ["board certified family medicine", "ABFM certified physician", "family medicine residency graduate"]
            ],
            "anthropology.yml": [
                # Strategy 1: Recent PhD focus
                ["recent PhD anthropology ethnographic research", "new anthropology doctorate fieldwork", "fresh anthropology PhD graduate"],
                # Strategy 2: Applied anthropology focus
                ["applied anthropology community research", "cultural anthropology policy analysis", "social anthropology practice"],
                # Strategy 3: Methodological focus
                ["ethnographic methods anthropologist", "qualitative research anthropology", "fieldwork anthropology expert"],
                # Strategy 4: Academic output focus
                ["published anthropologist research papers", "anthropology conference presentations", "anthropological publications"],
                # Strategy 5: Interdisciplinary focus
                ["interdisciplinary anthropologist", "anthropology social sciences", "cultural studies anthropology"]
            ],
            "quantitative_finance.yml": [
                # Strategy 1: Python/programming focus
                ["quantitative analyst Python programming", "quant developer financial modeling", "Python quantitative finance expert"],
                # Strategy 2: MBA + experience focus
                ["MBA quantitative finance analyst", "top university quant researcher", "prestigious MBA quant finance"],
                # Strategy 3: High-stakes experience focus
                ["investment bank quantitative analyst", "hedge fund quant researcher", "trading firm quantitative developer"],
                # Strategy 4: Technical skills focus
                ["derivatives pricing quantitative analyst", "risk modeling quant expert", "algorithmic trading quantitative"],
                # Strategy 5: Education + experience focus
                ["PhD quantitative finance professional", "masters quantitative finance expert", "advanced degree quant analyst"]
            ],
            "tax_lawyer.yml": [
                # Strategy 1: Corporate tax focus
                ["corporate tax attorney transactions", "business tax lawyer M&A", "transaction tax counsel corporate"],
                # Strategy 2: IRS expertise focus
                ["IRS audit defense attorney", "tax controversy lawyer", "IRS disputes tax counsel"],
                # Strategy 3: Legal writing focus
                ["tax lawyer legal writing expertise", "tax attorney published author", "legal opinions tax counsel"],
                # Strategy 4: Big law focus
                ["large firm tax attorney", "major law firm tax lawyer", "big law tax counsel experience"],
                # Strategy 5: JD + experience focus
                ["JD tax lawyer experienced", "law school graduate tax attorney", "bar admitted tax counsel"]
            ]
        }
        
        category_strategies = strategies.get(category, [["professional experienced expert"]])
        strategy_index = strategy_num % len(category_strategies)
        return category_strategies[strategy_index]
    
    def optimize_category_aggressive(self, category: str) -> bool:
        """Aggressively optimize a specific category with multiple strategies"""
        self.log(f"🎯 AGGRESSIVE OPTIMIZATION: {category}")
        
        success_count = 0
        
        for strategy_num in range(self.strategies_per_category):
            try:
                search_terms = self.generate_advanced_search_terms(category, strategy_num)
                
                for attempt, search_term in enumerate(search_terms, 1):
                    self.log(f"📝 Strategy {strategy_num+1}, Attempt {attempt}: {search_term}")
                    
                    # Use intelligent validator
                    query = SearchQuery(
                        query_text=search_term,
                        job_category=category,
                        strategy=SearchStrategy.HYBRID
                    )
                    
                    try:
                        candidates, validation_results = self.intelligent_validator.orchestrate_search(query)
                        
                        if validation_results and validation_results[-1].score > 0.5:
                            success_count += 1
                            self.log(f"💡 Search improved: score {validation_results[-1].score:.2f}")
                        else:
                            self.log(f"📊 Search completed: score {validation_results[-1].score:.2f}" if validation_results else "📊 Search completed")
                    except Exception as e:
                        self.log(f"⚠️ Validation error: {e}")
                    
                    # Short delay between attempts
                    time.sleep(self.base_delay)
                
                # Delay between strategies
                time.sleep(10)
                
            except Exception as e:
                self.log(f"❌ Error in strategy {strategy_num+1} for {category}: {e}")
        
        self.log(f"✅ Completed {success_count}/{self.strategies_per_category} strategies for {category}")
        return success_count > 0
    
    def check_completion_status(self) -> Dict[str, any]:
        """Check completion status"""
        scores = self.get_current_scores()
        if not scores:
            return {"completed": False, "scores": {}}
        
        below_30 = {k: v for k, v in scores.items() if v < 30.0}
        above_30 = {k: v for k, v in scores.items() if v >= 30.0}
        
        progress_made = False
        if self.last_scores:
            for cat in self.target_categories.keys():
                if cat in scores and cat in self.last_scores:
                    if scores[cat] > self.last_scores[cat]:
                        progress_made = True
                        self.log(f"📈 PROGRESS: {cat} improved from {self.last_scores[cat]:.2f} to {scores[cat]:.2f}")
        
        self.last_scores = scores.copy()
        
        return {
            "completed": len(below_30) == 0,
            "scores": scores,
            "below_30": below_30,
            "above_30": above_30,
            "progress_made": progress_made,
            "success_rate": len(above_30) / len(scores) if scores else 0
        }
    
    def run_night_optimization(self):
        """Run the overnight optimization"""
        self.log("🌙 STARTING AGGRESSIVE NIGHT OPTIMIZATION")
        self.log(f"⏰ Target runtime: Until all categories > 30 or {self.max_iterations} iterations")
        
        try:
            while self.iteration < self.max_iterations:
                self.iteration += 1
                self.log(f"\n🔄 NIGHT ITERATION {self.iteration}/{self.max_iterations}")
                
                # Check status every few iterations
                if self.iteration % self.evaluation_interval == 0:
                    status = self.check_completion_status()
                    
                    if status["completed"]:
                        self.log("🎉 ALL CATEGORIES ABOVE 30! OPTIMIZATION COMPLETE!")
                        self.log("🎊 Proceeding to final submission...")
                        return True
                    
                    self.log(f"📊 Current status: {len(status['above_30'])}/10 above 30")
                    self.log(f"📈 Success rate: {status['success_rate']*100:.1f}%")
                    
                    if status["below_30"]:
                        self.log("❌ Still need work:")
                        for cat, score in status["below_30"].items():
                            self.log(f"   • {cat}: {score:.2f}")
                
                # Optimize each target category
                for category in self.target_categories.keys():
                    self.optimize_category_aggressive(category)
                    time.sleep(15)  # Brief pause between categories
                
                # Progress update
                runtime = datetime.now() - self.start_time
                self.log(f"⏱️ Runtime: {str(runtime).split('.')[0]} | Iteration {self.iteration} complete")
                
                # Longer pause between iterations
                time.sleep(60)
            
            # Final check after max iterations
            self.log("⚠️ Maximum iterations reached. Final status check...")
            final_status = self.check_completion_status()
            
            if final_status["completed"]:
                self.log("🎉 OPTIMIZATION COMPLETED AT MAXIMUM ITERATIONS!")
                return True
            else:
                self.log(f"📊 Final result: {len(final_status['above_30'])}/10 above 30")
                self.log("🔄 Consider running additional optimization if time permits")
                return False
                
        except KeyboardInterrupt:
            self.log("⚠️ OPTIMIZATION INTERRUPTED BY USER")
            return False
        except Exception as e:
            self.log(f"❌ OPTIMIZATION ERROR: {e}")
            return False
        finally:
            self.log("🏁 NIGHT OPTIMIZATION SESSION COMPLETE")

if __name__ == "__main__":
    optimizer = AggressiveNightOptimizer()
    success = optimizer.run_night_optimization()
    
    if success:
        print("\n🎉 Ready for final submission!")
    else:
        print("\n📊 Optimization complete - check results") 