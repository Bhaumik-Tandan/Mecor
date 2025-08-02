#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE AUTOMATED OPTIMIZER
====================================
Continuously optimizes categories until they reach 30+ and submits to grade API.
Features:
- Continuous optimization loop
- Automatic grade API submission when categories reach 30
- Progress tracking and recovery
- Rate limit handling
- GitHub integration
- Computer sleep prevention
"""

import json
import os
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Import our existing modules
from src.main import SearchAgent
from src.agents.validation_agent import IntelligentValidationAgent
from src.services.evaluation_service import SafeEvaluationService
from src.services.search_service import SearchService
from src.config.settings import config

class ComprehensiveOptimizer:
    def __init__(self):
        self.setup_logging()
        self.search_agent = SearchAgent()
        self.evaluation_service = SafeEvaluationService()
        self.search_service = SearchService()
        self.intelligent_validator = IntelligentValidationAgent()
        
        self.target_categories = [
            "tax_lawyer.yml",
            "anthropology.yml", 
            "biology_expert.yml",
            "quantitative_finance.yml",
            "doctors_md.yml",
            "junior_corporate_lawyer.yml"
        ]
        
        self.progress_file = "comprehensive_progress.json"
        self.submitted_categories = set()
        self.target_score = 30.0
        
        # Load previous progress
        self.load_progress()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler('logs/comprehensive_optimizer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_progress(self):
        """Load previous progress from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.submitted_categories = set(data.get('submitted_categories', []))
                    self.logger.info(f"📊 Loaded progress: {len(self.submitted_categories)} categories already submitted")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load progress: {e}")
                
    def save_progress(self, current_scores: Dict[str, float]):
        """Save current progress to file"""
        progress_data = {
            'timestamp': datetime.now().isoformat(),
            'submitted_categories': list(self.submitted_categories),
            'current_scores': current_scores,
            'target_score': self.target_score
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
            
    def prevent_sleep(self):
        """Prevent computer from sleeping (macOS)"""
        try:
            subprocess.Popen(['caffeinate', '-d'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.logger.info("☕ Computer sleep prevention activated")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not prevent sleep: {e}")
            
    def get_current_scores(self) -> Dict[str, float]:
        """Get current scores with rate limit handling"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"📊 Getting current scores (attempt {attempt + 1}/{max_retries})")
                
                # Add delay to respect rate limits
                if attempt > 0:
                    delay = min(300, 60 * (2 ** attempt))  # Exponential backoff, max 5 min
                    self.logger.info(f"⏱️ Rate limit delay: {delay}s")
                    time.sleep(delay)
                
                result = self.search_agent.run_evaluation()
                
                if result and 'scores' in result:
                    scores = {}
                    for category, score in result['scores'].items():
                        if category in self.target_categories:
                            scores[category] = float(score)
                    
                    self.logger.info(f"✅ Current scores: {scores}")
                    return scores
                    
            except Exception as e:
                self.logger.error(f"❌ Error getting scores: {e}")
                if "429" in str(e) or "Too Many Requests" in str(e):
                    delay = min(600, 120 * (attempt + 1))  # Up to 10 minutes for 429
                    self.logger.warning(f"🚫 Rate limited. Waiting {delay}s...")
                    time.sleep(delay)
                    continue
                    
        self.logger.error("❌ Failed to get current scores after all retries")
        return {}
        
    def optimize_category(self, category: str, current_score: float) -> Optional[float]:
        """Optimize a single category with advanced strategies"""
        self.logger.info(f"🎯 OPTIMIZING: {category} (current: {current_score:.2f})")
        
        # Ultra-premium search terms for each category
        search_strategies = {
            "tax_lawyer.yml": [
                "Senior Tax Attorney Big Four firms", 
                "Tax Partner international law firms",
                "Corporate Tax Director Fortune 500",
                "Tax Specialist CPA JD dual degree"
            ],
            "anthropology.yml": [
                "Cultural Anthropologist PhD university professor",
                "Applied Anthropologist research director",
                "Medical Anthropologist public health",
                "Digital Anthropologist technology research"
            ],
            "biology_expert.yml": [
                "Molecular Biologist PhD research scientist",
                "Computational Biology Director pharmaceutical",
                "Systems Biology Professor university",
                "Biotechnology Research Leader industry"
            ],
            "quantitative_finance.yml": [
                "Quantitative Analyst hedge fund director",
                "Financial Engineer derivatives specialist",
                "Risk Management Quant investment bank",
                "Algorithmic Trading Developer systematic"
            ],
            "doctors_md.yml": [
                "Board Certified Physician specialist",
                "Chief Medical Officer healthcare system",
                "Academic Medicine Professor MD PhD",
                "Physician Researcher clinical trials"
            ],
            "junior_corporate_lawyer.yml": [
                "Corporate Associate top law firm",
                "Securities Attorney junior partner",
                "M&A Lawyer corporate transactions",
                "Commercial Litigation Associate"
            ]
        }
        
        strategies = search_strategies.get(category, [f"Expert professional {category.replace('.yml', '').replace('_', ' ')}"])
        
        best_score = current_score
        
        for i, search_term in enumerate(strategies):
            try:
                self.logger.info(f"📍 Strategy {i+1}/{len(strategies)}: {search_term}")
                
                # Rate limit delay
                if i > 0:
                    time.sleep(30)  # 30s between strategies
                
                from src.models.candidate import SearchQuery, SearchStrategy
                
                search_query = SearchQuery(
                    query_text=search_term,
                    job_category=category,
                    strategy=SearchStrategy.HYBRID,
                    max_candidates=50
                )
                
                # Run orchestrated search
                result = self.intelligent_validator.orchestrate_search(search_query)
                
                if result:
                    # Get updated score
                    time.sleep(30)  # Wait before score check
                    scores = self.get_current_scores()
                    if scores and category in scores:
                        new_score = scores[category]
                        improvement = new_score - best_score
                        
                        self.logger.info(f"📈 Score: {new_score:.2f} (change: {improvement:+.2f})")
                        
                        if new_score > best_score:
                            best_score = new_score
                            self.logger.info(f"🎉 NEW BEST: {best_score:.2f}")
                            
                        if new_score >= self.target_score:
                            self.logger.info(f"🏆 TARGET REACHED: {new_score:.2f} >= {self.target_score}")
                            return new_score
                            
            except Exception as e:
                self.logger.error(f"❌ Strategy {i+1} failed: {e}")
                continue
                
        return best_score
        
    def submit_to_grade_api(self, category: str) -> bool:
        """Submit a single category to the grade API"""
        try:
            self.logger.info(f"🚀 SUBMITTING to grade API: {category}")
            
            # Get candidates for this category
            candidates = self.get_category_candidates(category)
            if len(candidates) < 10:
                self.logger.error(f"❌ Not enough candidates for {category}: {len(candidates)}")
                return False
                
            # Prepare payload
            payload = {
                "config_candidates": {
                    category: candidates[:10]  # Exactly 10 candidates
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'bhaumik.tandan@gmail.com'
            }
            
            response = requests.post(
                 'https://mercor-dev--search-eng-interview.modal.run/grade',
                 headers=headers,
                 json=payload,
                 timeout=60
             )
            
            if response.status_code == 200:
                self.logger.info(f"✅ Successfully submitted {category} to grade API")
                self.submitted_categories.add(category)
                return True
            else:
                self.logger.error(f"❌ Grade API error for {category}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error submitting {category}: {e}")
            return False
            
    def get_category_candidates(self, category: str) -> List[str]:
        """Get candidates for a specific category using multiple strategies"""
        from src.models.candidate import SearchQuery, SearchStrategy
        
        all_candidates = set()
        
        strategies = [
            SearchStrategy.HYBRID,
            SearchStrategy.VECTOR_ONLY, 
            SearchStrategy.BM25_ONLY
        ]
        
        for strategy in strategies:
            try:
                self.logger.info(f"🔍 Getting candidates with {strategy.value} strategy")
                
                query = SearchQuery(
                    query_text=category.replace("_", " ").replace(".yml", ""),
                    job_category=category,
                    strategy=strategy,
                    max_candidates=30
                )
                
                candidates = self.search_service.search_candidates(query, strategy)
                if candidates:
                    candidate_ids = [c.id for c in candidates[:20]]  # Take top 20 from each
                    all_candidates.update(candidate_ids)
                    
                time.sleep(15)  # Rate limit delay
                
            except Exception as e:
                self.logger.warning(f"⚠️ Strategy {strategy.value} failed for {category}: {e}")
                continue
                
        candidates_list = list(all_candidates)
        self.logger.info(f"📋 Collected {len(candidates_list)} unique candidates for {category}")
        return candidates_list
        
    def push_to_github(self):
        """Push current progress to GitHub"""
        try:
            self.logger.info("📤 Pushing to GitHub...")
            
            # Add and commit changes
            subprocess.run(['git', 'add', '.'], check=True)
            commit_msg = f"Automated optimization progress - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            subprocess.run(['git', 'push', 'origin', 'master'], check=True)
            
            self.logger.info("✅ Successfully pushed to GitHub")
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"⚠️ Git operation failed: {e}")
        except Exception as e:
            self.logger.error(f"❌ GitHub push error: {e}")
            
    def run_continuous_optimization(self):
        """Main continuous optimization loop"""
        self.logger.info("🚀 STARTING COMPREHENSIVE AUTOMATED OPTIMIZATION")
        self.logger.info("=" * 80)
        
        # Prevent computer sleep
        self.prevent_sleep()
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                self.logger.info(f"\n🔄 ITERATION {iteration}")
                self.logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Get current scores
                current_scores = self.get_current_scores()
                if not current_scores:
                    self.logger.warning("⚠️ Could not get scores, waiting 5 minutes...")
                    time.sleep(300)
                    continue
                    
                # Save progress
                self.save_progress(current_scores)
                
                # Check which categories need optimization
                categories_to_optimize = []
                categories_ready_for_submission = []
                
                for category in self.target_categories:
                    if category in current_scores:
                        score = current_scores[category]
                        
                        if score >= self.target_score and category not in self.submitted_categories:
                            categories_ready_for_submission.append(category)
                        elif score < self.target_score:
                            categories_to_optimize.append((category, score))
                            
                # Submit ready categories to grade API
                for category in categories_ready_for_submission:
                    if self.submit_to_grade_api(category):
                        self.logger.info(f"🎊 {category} SUBMITTED TO GRADE API!")
                    time.sleep(60)  # Wait between submissions
                    
                # Optimize categories that need improvement
                if categories_to_optimize:
                    # Sort by proximity to target (closest first)
                    categories_to_optimize.sort(key=lambda x: self.target_score - x[1])
                    
                    self.logger.info(f"🎯 Categories to optimize: {len(categories_to_optimize)}")
                    
                    for category, score in categories_to_optimize:
                        self.logger.info(f"\n🔧 OPTIMIZING: {category} (current: {score:.2f})")
                        
                        new_score = self.optimize_category(category, score)
                        
                        if new_score and new_score >= self.target_score:
                            self.logger.info(f"🏆 {category} REACHED TARGET: {new_score:.2f}")
                            # Will be submitted in next iteration
                            
                        # Rate limit delay between categories
                        time.sleep(120)  # 2 minutes between categories
                        
                else:
                    self.logger.info("🎉 ALL CATEGORIES OPTIMIZED AND SUBMITTED!")
                    
                # Push progress to GitHub every 3 iterations
                if iteration % 3 == 0:
                    self.push_to_github()
                    
                # Status summary
                completed = len(self.submitted_categories)
                remaining = len(self.target_categories) - completed
                self.logger.info(f"\n📊 STATUS: {completed}/{len(self.target_categories)} submitted, {remaining} remaining")
                
                # Check if all done
                if completed >= len(self.target_categories):
                    self.logger.info("🎊 ALL CATEGORIES COMPLETED! MISSION ACCOMPLISHED!")
                    self.push_to_github()
                    break
                    
                # Wait before next iteration (longer delay)
                self.logger.info("⏱️ Waiting 10 minutes before next iteration...")
                time.sleep(600)  # 10 minutes between full iterations
                
            except KeyboardInterrupt:
                self.logger.info("⏸️ Optimization paused by user")
                self.save_progress(current_scores if 'current_scores' in locals() else {})
                break
                
            except Exception as e:
                self.logger.error(f"❌ Unexpected error in iteration {iteration}: {e}")
                time.sleep(300)  # 5 minutes on error
                continue

if __name__ == "__main__":
    optimizer = ComprehensiveOptimizer()
    optimizer.run_continuous_optimization() 