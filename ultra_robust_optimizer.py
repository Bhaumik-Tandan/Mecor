#!/usr/bin/env python3
"""
🔥 ULTRA-ROBUST 2-HOUR COMPREHENSIVE OPTIMIZER
==============================================
Enhanced version designed for extended 2+ hour continuous operation.
Features maximum stability, error recovery, and progress preservation.
"""

import json
import os
import time
import requests
import subprocess
import psutil
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import traceback

# Import our existing modules
from src.main import SearchAgent
from src.agents.validation_agent import IntelligentValidationAgent
from src.services.evaluation_service import SafeEvaluationService
from src.services.search_service import SearchService
from src.config.settings import config

class UltraRobustOptimizer:
    def __init__(self):
        self.setup_comprehensive_logging()
        self.start_time = datetime.now()
        self.target_duration = timedelta(hours=2, minutes=10)  # 2h 10m for buffer
        self.initialize_services()
        
        self.target_categories = [
            "tax_lawyer.yml",
            "anthropology.yml", 
            "biology_expert.yml",
            "quantitative_finance.yml",
            "doctors_md.yml",
            "junior_corporate_lawyer.yml"
        ]
        
        self.progress_file = "ultra_robust_progress.json"
        self.checkpoint_file = "optimizer_checkpoint.json"
        self.submitted_categories = set()
        self.target_score = 30.0
        self.max_consecutive_failures = 5
        self.consecutive_failures = 0
        self.last_successful_iteration = datetime.now()
        
        # Enhanced rate limiting
        self.base_delay = 60  # 1 minute base delay
        self.evaluation_delay = 300  # 5 minutes between evaluations
        self.api_failure_delay = 600  # 10 minutes after API failures
        
        # Load previous progress
        self.load_progress()
        self.setup_signal_handlers()
        
    def setup_comprehensive_logging(self):
        """Setup multi-level logging for ultra-robust operation"""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Main logger
        self.logger = logging.getLogger('UltraRobustOptimizer')
        self.logger.setLevel(logging.INFO)
        
        # File handler with rotation
        log_filename = f"logs/ultra_robust_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Error logger
        self.error_logger = logging.getLogger('ErrorLogger')
        error_handler = logging.FileHandler('logs/ultra_robust_errors.log')
        error_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_handler)
        
    def initialize_services(self):
        """Initialize services with enhanced error handling"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.search_agent = SearchAgent()
                self.evaluation_service = SafeEvaluationService()
                self.search_service = SearchService()
                self.intelligent_validator = IntelligentValidationAgent()
                
                self.logger.info("✅ All services initialized successfully")
                return
                
            except Exception as e:
                self.logger.error(f"❌ Service initialization attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(10 * (attempt + 1))
                else:
                    raise Exception(f"Failed to initialize services after {max_retries} attempts")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
            self.save_checkpoint()
            self.push_to_github("Emergency checkpoint before shutdown")
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def prevent_sleep_ultra(self):
        """Ultra-robust sleep prevention with monitoring"""
        try:
            # Kill any existing caffeinate processes
            subprocess.run(['pkill', '-f', 'caffeinate'], capture_output=True)
            time.sleep(2)
            
            # Start new caffeinate process
            self.caffeinate_process = subprocess.Popen(
                ['caffeinate', '-d', '-i', '-m', '-s'], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            
            self.logger.info("☕ Ultra-robust sleep prevention activated (display, idle, disk, system)")
            
            # Verify it's working
            time.sleep(2)
            if self.caffeinate_process.poll() is None:
                self.logger.info(f"✅ Sleep prevention confirmed (PID: {self.caffeinate_process.pid})")
            else:
                self.logger.warning("⚠️ Sleep prevention process may have failed")
                
        except Exception as e:
            self.logger.error(f"❌ Sleep prevention setup failed: {e}")
    
    def monitor_system_resources(self):
        """Monitor system resources and log warnings"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_free_gb = disk.free / (1024**3)
            
            self.logger.info(f"📊 Resources: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}% ({memory_available_gb:.1f}GB free), Disk {disk_free_gb:.1f}GB free")
            
            # Warnings
            if cpu_percent > 80:
                self.logger.warning(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
            if memory_percent > 90:
                self.logger.warning(f"⚠️ High memory usage: {memory_percent:.1f}%")
            if disk_free_gb < 1:
                self.logger.warning(f"⚠️ Low disk space: {disk_free_gb:.1f}GB")
                
        except Exception as e:
            self.logger.error(f"❌ Resource monitoring failed: {e}")
    
    def load_progress(self):
        """Load previous progress with enhanced error handling"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.submitted_categories = set(data.get('submitted_categories', []))
                    self.consecutive_failures = data.get('consecutive_failures', 0)
                    
                    last_success_str = data.get('last_successful_iteration')
                    if last_success_str:
                        self.last_successful_iteration = datetime.fromisoformat(last_success_str)
                    
                    self.logger.info(f"📊 Loaded progress: {len(self.submitted_categories)} submitted, {self.consecutive_failures} consecutive failures")
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Could not load progress: {e}")
            
    def save_progress(self, current_scores: Dict[str, float]):
        """Save progress with enhanced data"""
        try:
            progress_data = {
                'timestamp': datetime.now().isoformat(),
                'submitted_categories': list(self.submitted_categories),
                'current_scores': current_scores,
                'target_score': self.target_score,
                'consecutive_failures': self.consecutive_failures,
                'last_successful_iteration': self.last_successful_iteration.isoformat(),
                'runtime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
                'target_duration_hours': self.target_duration.total_seconds() / 3600
            }
            
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
                
            self.logger.info(f"💾 Progress saved: {len(self.submitted_categories)}/6 completed")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save progress: {e}")
    
    def save_checkpoint(self):
        """Save detailed checkpoint for recovery"""
        try:
            checkpoint_data = {
                'timestamp': datetime.now().isoformat(),
                'start_time': self.start_time.isoformat(),
                'runtime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'submitted_categories': list(self.submitted_categories),
                'consecutive_failures': self.consecutive_failures,
                'last_successful_iteration': self.last_successful_iteration.isoformat(),
                'target_categories': self.target_categories,
                'system_info': {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_free_gb': psutil.disk_usage('/').free / (1024**3)
                }
            }
            
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
                
            self.logger.info("🔒 Checkpoint saved successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save checkpoint: {e}")
    
    def get_current_scores_ultra_safe(self) -> Dict[str, float]:
        """Ultra-safe score retrieval with extensive error handling"""
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"📊 Getting current scores (attempt {attempt + 1}/{max_retries})")
                
                # Progressive delay
                if attempt > 0:
                    delay = min(600, self.base_delay * (2 ** attempt))
                    self.logger.info(f"⏱️ Ultra-safe delay: {delay}s")
                    time.sleep(delay)
                
                # Monitor resources before API call
                self.monitor_system_resources()
                
                result = self.search_agent.run_evaluation()
                
                if result and 'scores' in result:
                    scores = {}
                    for category, score in result['scores'].items():
                        if category in self.target_categories:
                            scores[category] = float(score)
                    
                    self.logger.info(f"✅ Retrieved scores: {scores}")
                    self.consecutive_failures = 0
                    self.last_successful_iteration = datetime.now()
                    return scores
                    
            except Exception as e:
                self.consecutive_failures += 1
                self.error_logger.error(f"Score retrieval attempt {attempt + 1} failed: {e}")
                self.error_logger.error(traceback.format_exc())
                
                if "429" in str(e) or "Too Many Requests" in str(e):
                    delay = min(1200, self.api_failure_delay * (attempt + 1))
                    self.logger.warning(f"🚫 Rate limited. Ultra-safe delay: {delay}s")
                    time.sleep(delay)
                elif "502" in str(e) or "503" in str(e):
                    delay = min(900, 300 * (attempt + 1))
                    self.logger.warning(f"🔄 Server error. Waiting {delay}s for recovery")
                    time.sleep(delay)
                else:
                    self.logger.error(f"❌ Unexpected error: {e}")
                    time.sleep(60 * (attempt + 1))
                    
        self.logger.error("❌ Failed to get scores after all ultra-safe retries")
        return {}
    
    def check_time_remaining(self) -> bool:
        """Check if we still have time remaining"""
        elapsed = datetime.now() - self.start_time
        remaining = self.target_duration - elapsed
        
        remaining_hours = remaining.total_seconds() / 3600
        self.logger.info(f"⏰ Time remaining: {remaining_hours:.2f} hours")
        
        if remaining_hours <= 0:
            self.logger.info("⏰ Target duration reached!")
            return False
            
        if remaining_hours < 0.5:  # Less than 30 minutes
            self.logger.warning(f"⚠️ Only {remaining_hours:.2f} hours remaining")
            
        return True
    
    def push_to_github(self, message: str = None):
        """Enhanced GitHub push with error handling"""
        try:
            if not message:
                runtime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
                message = f"Ultra-robust optimizer progress - {runtime_hours:.1f}h runtime, {len(self.submitted_categories)}/6 completed"
            
            self.logger.info("📤 Pushing progress to GitHub...")
            
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', message], check=True, capture_output=True)
            subprocess.run(['git', 'push', 'origin', 'master'], check=True, capture_output=True)
            
            self.logger.info("✅ Successfully pushed to GitHub")
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"⚠️ Git operation failed: {e}")
        except Exception as e:
            self.logger.error(f"❌ GitHub push error: {e}")
    
    def submit_to_grade_api_ultra_safe(self, category: str) -> bool:
        """Ultra-safe grade API submission"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🚀 ULTRA-SAFE SUBMISSION to grade API: {category} (attempt {attempt + 1})")
                
                # Get candidates with multiple strategies
                candidates = self.get_category_candidates_robust(category)
                
                if len(candidates) < 10:
                    self.logger.error(f"❌ Insufficient candidates for {category}: {len(candidates)}")
                    return False
                
                payload = {
                    "config_candidates": {
                        category: candidates[:10]
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
                    timeout=120  # Longer timeout
                )
                
                if response.status_code == 200:
                    self.logger.info(f"🎊 Successfully submitted {category} to grade API!")
                    self.submitted_categories.add(category)
                    return True
                else:
                    self.logger.error(f"❌ Grade API error for {category}: {response.status_code} - {response.text}")
                    
            except Exception as e:
                self.logger.error(f"❌ Submission attempt {attempt + 1} failed for {category}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(60 * (attempt + 1))
                    
        return False
    
    def get_category_candidates_robust(self, category: str) -> List[str]:
        """Robust candidate collection with multiple fallback strategies"""
        from src.models.candidate import SearchQuery, SearchStrategy
        
        all_candidates = set()
        strategies = [SearchStrategy.HYBRID, SearchStrategy.VECTOR_ONLY, SearchStrategy.BM25_ONLY]
        
        for strategy in strategies:
            try:
                self.logger.info(f"🔍 Robust candidate search: {category} with {strategy.value}")
                
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
                    self.logger.info(f"✅ Added {len(candidate_ids)} candidates from {strategy.value}")
                    
                time.sleep(30)  # Conservative delay
                
            except Exception as e:
                self.logger.warning(f"⚠️ Strategy {strategy.value} failed for {category}: {e}")
                time.sleep(10)
                continue
                
        candidates_list = list(all_candidates)
        self.logger.info(f"📋 Total collected: {len(candidates_list)} unique candidates for {category}")
        return candidates_list
    
    def run_ultra_robust_optimization(self):
        """Main ultra-robust 2-hour optimization loop"""
        self.logger.info("🔥 STARTING ULTRA-ROBUST 2-HOUR OPTIMIZATION")
        self.logger.info("=" * 80)
        self.logger.info(f"⏰ Target duration: {self.target_duration}")
        self.logger.info(f"🎯 Target categories: {len(self.target_categories)}")
        
        # Setup environment
        self.prevent_sleep_ultra()
        
        iteration = 0
        
        try:
            while self.check_time_remaining():
                iteration += 1
                self.logger.info(f"\n🔄 ULTRA-ROBUST ITERATION {iteration}")
                self.logger.info(f"⏰ Runtime: {(datetime.now() - self.start_time).total_seconds() / 3600:.2f} hours")
                
                # Save checkpoint every iteration
                self.save_checkpoint()
                
                # Monitor system health
                self.monitor_system_resources()
                
                # Check for excessive failures
                if self.consecutive_failures >= self.max_consecutive_failures:
                    self.logger.warning(f"⚠️ Too many consecutive failures ({self.consecutive_failures}). Extended recovery delay...")
                    time.sleep(self.api_failure_delay)
                    self.consecutive_failures = 0
                
                # Get current scores with ultra-safe method
                current_scores = self.get_current_scores_ultra_safe()
                
                if not current_scores:
                    self.logger.warning("⚠️ Could not get scores. Extended wait before retry...")
                    time.sleep(self.evaluation_delay)
                    continue
                
                # Save progress
                self.save_progress(current_scores)
                
                # Check which categories are ready for submission
                categories_ready = []
                categories_need_work = []
                
                for category in self.target_categories:
                    if category in current_scores:
                        score = current_scores[category]
                        
                        if score >= self.target_score and category not in self.submitted_categories:
                            categories_ready.append((category, score))
                        elif score < self.target_score:
                            categories_need_work.append((category, score))
                
                # Submit ready categories
                for category, score in categories_ready:
                    self.logger.info(f"🎯 Category {category} ready for submission: {score:.2f}")
                    if self.submit_to_grade_api_ultra_safe(category):
                        self.logger.info(f"🎊 {category} SUCCESSFULLY SUBMITTED!")
                    time.sleep(120)  # 2 minutes between submissions
                
                # Log status
                completed = len(self.submitted_categories)
                remaining = len(self.target_categories) - completed
                
                self.logger.info(f"\n📊 ULTRA-ROBUST STATUS:")
                self.logger.info(f"   ✅ Completed: {completed}/{len(self.target_categories)}")
                self.logger.info(f"   🔄 Remaining: {remaining}")
                self.logger.info(f"   ⚠️ Consecutive failures: {self.consecutive_failures}")
                
                # Check if mission complete
                if completed >= len(self.target_categories):
                    self.logger.info("🎊 MISSION ACCOMPLISHED! ALL CATEGORIES SUBMITTED!")
                    self.push_to_github("🎊 Mission completed - all categories submitted!")
                    break
                
                # Push to GitHub every 3 iterations
                if iteration % 3 == 0:
                    self.push_to_github()
                
                # Extended delay between iterations for stability
                self.logger.info(f"⏱️ Ultra-robust delay: {self.evaluation_delay}s before next iteration")
                time.sleep(self.evaluation_delay)
                
        except KeyboardInterrupt:
            self.logger.info("⏸️ Ultra-robust optimization interrupted by user")
            
        except Exception as e:
            self.logger.error(f"❌ Critical error in ultra-robust optimization: {e}")
            self.error_logger.error(traceback.format_exc())
            
        finally:
            # Final cleanup
            self.save_checkpoint()
            runtime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            final_message = f"Ultra-robust optimizer finished - {runtime_hours:.2f}h runtime, {len(self.submitted_categories)}/6 completed"
            self.push_to_github(final_message)
            
            # Stop sleep prevention
            if hasattr(self, 'caffeinate_process'):
                try:
                    self.caffeinate_process.terminate()
                    self.logger.info("☕ Sleep prevention deactivated")
                except:
                    pass
            
            self.logger.info(f"🏁 Ultra-robust optimization completed after {runtime_hours:.2f} hours")

if __name__ == "__main__":
    optimizer = UltraRobustOptimizer()
    optimizer.run_ultra_robust_optimization() 