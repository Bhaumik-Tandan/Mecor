#!/usr/bin/env python3
"""
👁️ AUTONOMOUS 2-HOUR MONITOR
============================
Comprehensive monitoring for 2+ hours while user is away.
Tracks optimizer progress, logs everything, handles completion.
"""

import os
import time
import subprocess
import json
from datetime import datetime, timedelta
import psutil

class Autonomous2HourMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=2, minutes=15)  # 2h 15m buffer
        self.log_file = "autonomous_monitor.log"
        self.status_file = "monitor_status.json"
        self.optimizer_pid = None
        self.last_log_size = 0
        self.iteration_count = 0
        self.check_interval = 60  # Check every minute
        
        self.init_monitoring()
        
    def init_monitoring(self):
        """Initialize monitoring system"""
        self.log(f"👁️ AUTONOMOUS 2-HOUR MONITOR STARTED")
        self.log(f"⏰ Start time: {self.start_time.strftime('%H:%M:%S')}")
        self.log(f"🎯 End time: {self.end_time.strftime('%H:%M:%S')}")
        self.log(f"⏱️ Duration: 2h 15m")
        self.log(f"🔍 Check interval: {self.check_interval}s")
        
        # Find optimizer process
        self.find_optimizer_process()
        
    def log(self, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"{timestamp} | {message}"
        print(log_msg)
        
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")
            
    def find_optimizer_process(self):
        """Find the focused optimizer process"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'focused_continuous_optimizer.py' in line and 'grep' not in line:
                    parts = line.split()
                    self.optimizer_pid = int(parts[1])
                    self.log(f"✅ Found optimizer process: PID {self.optimizer_pid}")
                    return True
                    
            self.log("❌ Optimizer process not found")
            return False
            
        except Exception as e:
            self.log(f"❌ Error finding optimizer process: {e}")
            return False
    
    def check_process_status(self) -> bool:
        """Check if optimizer process is still running"""
        if not self.optimizer_pid:
            return False
            
        try:
            process = psutil.Process(self.optimizer_pid)
            cpu_percent = process.cpu_percent()
            memory_percent = process.memory_percent()
            
            self.log(f"📊 Process health: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%")
            return True
            
        except psutil.NoSuchProcess:
            self.log("❌ Optimizer process stopped")
            return False
        except Exception as e:
            self.log(f"⚠️ Error checking process: {e}")
            return False
    
    def check_log_activity(self) -> dict:
        """Check optimizer log for activity and progress"""
        activity_info = {
            'log_size': 0,
            'growth': 0,
            'last_line': '',
            'iteration_detected': False,
            'score_extraction_status': 'unknown'
        }
        
        try:
            if os.path.exists('optimizer_output.log'):
                # Check log size
                current_size = os.path.getsize('optimizer_output.log')
                growth = current_size - self.last_log_size
                self.last_log_size = current_size
                
                activity_info['log_size'] = current_size
                activity_info['growth'] = growth
                
                # Read last few lines
                with open('optimizer_output.log', 'r') as f:
                    lines = f.readlines()
                    
                if lines:
                    activity_info['last_line'] = lines[-1].strip()
                    
                    # Check last 10 lines for patterns
                    recent_lines = lines[-10:]
                    recent_text = ' '.join(recent_lines)
                    
                    # Detect iterations
                    if 'ITERATION' in recent_text:
                        activity_info['iteration_detected'] = True
                        
                    # Check score extraction status
                    if 'Failed to get scores' in recent_text:
                        activity_info['score_extraction_status'] = 'failing'
                    elif 'Successfully extracted:' in recent_text:
                        activity_info['score_extraction_status'] = 'success'
                    elif 'Getting current scores' in recent_text:
                        activity_info['score_extraction_status'] = 'attempting'
                        
                self.log(f"📈 Log size: {current_size} bytes (+{growth})")
                if activity_info['last_line']:
                    self.log(f"📝 Latest: {activity_info['last_line']}")
                    
        except Exception as e:
            self.log(f"❌ Error checking log: {e}")
            
        return activity_info
    
    def check_system_resources(self):
        """Monitor system resources"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.log(f"💻 System: CPU {cpu:.1f}%, Memory {memory.percent:.1f}%, Disk {disk.free/(1024**3):.1f}GB free")
            
            # Warnings
            if cpu > 80:
                self.log(f"⚠️ HIGH CPU: {cpu:.1f}%")
            if memory.percent > 90:
                self.log(f"⚠️ HIGH MEMORY: {memory.percent:.1f}%")
            if disk.free/(1024**3) < 1:
                self.log(f"⚠️ LOW DISK: {disk.free/(1024**3):.1f}GB")
                
        except Exception as e:
            self.log(f"❌ Resource monitoring error: {e}")
    
    def check_for_completion(self) -> bool:
        """Check if optimization has completed successfully"""
        try:
            if os.path.exists('optimizer_output.log'):
                with open('optimizer_output.log', 'r') as f:
                    content = f.read()
                    
                # Look for completion indicators
                if 'ALL CATEGORIES ABOVE 30!' in content:
                    self.log("🎊 COMPLETION DETECTED: ALL CATEGORIES ABOVE 30!")
                    return True
                elif 'MISSION ACCOMPLISHED' in content:
                    self.log("🎊 COMPLETION DETECTED: MISSION ACCOMPLISHED!")
                    return True
                elif 'SUCCESS! ALL CATEGORIES SUBMITTED' in content:
                    self.log("🎊 COMPLETION DETECTED: SUBMITTED TO GRADE API!")
                    return True
                    
        except Exception as e:
            self.log(f"❌ Error checking completion: {e}")
            
        return False
    
    def save_status(self, status_data: dict):
        """Save current status to file"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2, default=str)
        except Exception as e:
            self.log(f"❌ Error saving status: {e}")
    
    def handle_completion(self):
        """Handle successful completion"""
        self.log("🎊 OPTIMIZER COMPLETED SUCCESSFULLY!")
        self.log("📊 Running final score check...")
        
        # Run Option 2 to verify final scores
        try:
            result = subprocess.run(['python', 'improved_score_extractor.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log("✅ Final score verification completed")
                self.log(f"📊 Output: {result.stdout[-500:]}")  # Last 500 chars
            else:
                self.log(f"⚠️ Score verification had issues: {result.stderr}")
                
        except Exception as e:
            self.log(f"❌ Final verification error: {e}")
    
    def handle_failure(self):
        """Handle optimizer failure - deploy Option 2"""
        self.log("❌ OPTIMIZER APPEARS TO HAVE FAILED")
        self.log("🔧 DEPLOYING OPTION 2: IMPROVED SCORE EXTRACTOR")
        
        try:
            # Kill stuck optimizer
            if self.optimizer_pid:
                subprocess.run(['kill', str(self.optimizer_pid)], capture_output=True)
                self.log(f"🛑 Stopped stuck optimizer (PID {self.optimizer_pid})")
            
            # Run improved extractor
            self.log("🚀 Running improved score extractor...")
            result = subprocess.run(['python', 'improved_score_extractor.py'], 
                                  capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                self.log("✅ Improved extractor completed successfully")
                self.log(f"📊 Output: {result.stdout[-1000:]}")  # Last 1000 chars
            else:
                self.log(f"❌ Improved extractor failed: {result.stderr}")
                
        except Exception as e:
            self.log(f"❌ Option 2 deployment error: {e}")
    
    def run_monitoring(self):
        """Main monitoring loop"""
        self.log("🔄 STARTING 2-HOUR MONITORING LOOP")
        
        check_count = 0
        last_activity_time = datetime.now()
        consecutive_no_activity = 0
        
        while datetime.now() < self.end_time:
            check_count += 1
            current_time = datetime.now()
            elapsed = current_time - self.start_time
            remaining = self.end_time - current_time
            
            self.log(f"\n🔍 CHECK #{check_count} - Elapsed: {elapsed.total_seconds()/3600:.1f}h, Remaining: {remaining.total_seconds()/3600:.1f}h")
            
            # Check process status
            process_running = self.check_process_status()
            
            # Check log activity
            activity = self.check_log_activity()
            
            # Check system resources
            self.check_system_resources()
            
            # Check for completion
            if self.check_for_completion():
                self.handle_completion()
                break
            
            # Detect inactivity
            if activity['growth'] > 0:
                last_activity_time = current_time
                consecutive_no_activity = 0
            else:
                consecutive_no_activity += 1
            
            # Handle various scenarios
            if not process_running:
                self.log("❌ Process stopped - may have completed or failed")
                if not self.check_for_completion():
                    self.handle_failure()
                break
                
            elif consecutive_no_activity >= 10:  # 10 minutes no activity
                self.log("⚠️ No log activity for 10+ minutes - possible hang")
                self.handle_failure()
                break
            
            # Save status
            status_data = {
                'timestamp': current_time,
                'check_count': check_count,
                'process_running': process_running,
                'optimizer_pid': self.optimizer_pid,
                'elapsed_hours': elapsed.total_seconds() / 3600,
                'remaining_hours': remaining.total_seconds() / 3600,
                'log_size': activity['log_size'],
                'last_activity': last_activity_time,
                'consecutive_no_activity': consecutive_no_activity,
                'score_extraction_status': activity['score_extraction_status']
            }
            
            self.save_status(status_data)
            
            # Sleep until next check
            self.log(f"💤 Sleeping {self.check_interval}s until next check...")
            time.sleep(self.check_interval)
        
        # Final status
        if datetime.now() >= self.end_time:
            self.log("⏰ 2-HOUR MONITORING PERIOD COMPLETED")
            self.log("📊 Running final status check...")
            
            if self.check_process_status():
                self.log("✅ Optimizer still running after 2+ hours")
            else:
                self.log("❌ Optimizer not running")
                
        self.log("👁️ AUTONOMOUS MONITORING FINISHED")

if __name__ == "__main__":
    monitor = Autonomous2HourMonitor()
    try:
        monitor.run_monitoring()
    except KeyboardInterrupt:
        monitor.log("⏸️ Monitoring interrupted by user")
    except Exception as e:
        monitor.log(f"❌ Critical monitoring error: {e}")
        import traceback
        monitor.log(traceback.format_exc()) 