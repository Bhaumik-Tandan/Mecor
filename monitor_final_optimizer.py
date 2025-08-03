#!/usr/bin/env python3
"""
👁️ REAL-TIME OPTIMIZER MONITOR
===============================
Live monitoring of the final targeted optimizer.
"""

import os
import time
import subprocess
import json
from datetime import datetime, timedelta
import psutil

class OptimizerMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.log_file = "final_optimizer_output.log"
        self.progress_file = "final_optimizer.log"
        self.last_log_size = 0
        self.last_progress_size = 0
        self.check_interval = 30  # seconds
        self.optimizer_pid = None
        self.iteration_count = 0
        
    def find_optimizer_process(self):
        """Find the running optimizer process"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'final_targeted_optimizer.py' in ' '.join(proc.info['cmdline'] or []):
                    return proc.info['pid']
        except:
            pass
        return None
    
    def get_process_status(self):
        """Get current process status"""
        self.optimizer_pid = self.find_optimizer_process()
        
        if self.optimizer_pid:
            try:
                proc = psutil.Process(self.optimizer_pid)
                cpu_percent = proc.cpu_percent()
                memory_percent = proc.memory_percent()
                runtime = datetime.now() - datetime.fromtimestamp(proc.create_time())
                
                return {
                    'running': True,
                    'pid': self.optimizer_pid,
                    'cpu': cpu_percent,
                    'memory': memory_percent,
                    'runtime': str(runtime).split('.')[0]
                }
            except:
                return {'running': False}
        else:
            return {'running': False}
    
    def get_latest_logs(self, num_lines=8):
        """Get latest log entries"""
        try:
            # Check main output log
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    return lines[-num_lines:] if lines else []
            
            # Check progress log
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    lines = f.readlines()
                    return lines[-num_lines:] if lines else []
                    
        except Exception as e:
            return [f"Error reading logs: {e}"]
        
        return ["No logs found yet..."]
    
    def check_log_activity(self):
        """Check for new log activity"""
        activity = False
        
        # Check main log
        if os.path.exists(self.log_file):
            current_size = os.path.getsize(self.log_file)
            if current_size > self.last_log_size:
                activity = True
                self.last_log_size = current_size
        
        # Check progress log
        if os.path.exists(self.progress_file):
            current_size = os.path.getsize(self.progress_file)
            if current_size > self.last_progress_size:
                activity = True
                self.last_progress_size = current_size
        
        return activity
    
    def extract_current_iteration(self, logs):
        """Extract current iteration from logs"""
        for line in reversed(logs):
            if "ITERATION" in line:
                try:
                    # Extract iteration number
                    parts = line.split("ITERATION")
                    if len(parts) > 1:
                        iteration = parts[1].strip().split()[0]
                        return int(iteration)
                except:
                    pass
        return 0
    
    def extract_current_scores(self, logs):
        """Extract any score information from logs"""
        scores = {}
        for line in reversed(logs):
            if ":" in line and any(cat in line for cat in ['doctors_md', 'anthropology', 'quantitative_finance', 'tax_lawyer']):
                try:
                    if '.yml:' in line or 'yml' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            category = parts[-2].split()[-1].replace('.yml', '')
                            score_part = parts[-1].strip()
                            # Try to extract number
                            import re
                            numbers = re.findall(r'\d+\.?\d*', score_part)
                            if numbers:
                                scores[category] = float(numbers[0])
                except:
                    pass
        return scores
    
    def get_system_resources(self):
        """Get system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu': cpu_percent,
                'memory': memory.percent,
                'disk': disk.percent
            }
        except:
            return {'cpu': 0, 'memory': 0, 'disk': 0}
    
    def print_status_update(self):
        """Print comprehensive status update"""
        current_time = datetime.now()
        runtime = current_time - self.start_time
        
        print(f"\n{'='*60}")
        print(f"👁️  OPTIMIZER MONITOR - {current_time.strftime('%H:%M:%S')}")
        print(f"⏱️  Monitor Runtime: {str(runtime).split('.')[0]}")
        print(f"{'='*60}")
        
        # Process Status
        status = self.get_process_status()
        if status['running']:
            print(f"🔄 OPTIMIZER STATUS: ✅ RUNNING")
            print(f"   📊 PID: {status['pid']}")
            print(f"   🖥️  CPU: {status['cpu']:.1f}%")
            print(f"   🧠 Memory: {status['memory']:.1f}%")
            print(f"   ⏱️  Runtime: {status['runtime']}")
        else:
            print(f"🔄 OPTIMIZER STATUS: ❌ NOT RUNNING")
        
        # System Resources
        resources = self.get_system_resources()
        print(f"\n💻 SYSTEM RESOURCES:")
        print(f"   🖥️  CPU: {resources['cpu']:.1f}%")
        print(f"   🧠 Memory: {resources['memory']:.1f}%")
        print(f"   💾 Disk: {resources['disk']:.1f}%")
        
        # Log Activity
        activity = self.check_log_activity()
        print(f"\n📝 LOG ACTIVITY: {'✅ ACTIVE' if activity else '⏸️  QUIET'}")
        
        # Latest Logs
        logs = self.get_latest_logs()
        if logs:
            print(f"\n📋 LATEST ACTIVITY:")
            for line in logs[-5:]:  # Show last 5 lines
                clean_line = line.strip()
                if clean_line:
                    print(f"   {clean_line}")
        
        # Extract iteration info
        current_iteration = self.extract_current_iteration(logs)
        if current_iteration > 0:
            print(f"\n🔄 CURRENT ITERATION: {current_iteration}")
        
        # Extract any scores
        scores = self.extract_current_scores(logs)
        if scores:
            print(f"\n📊 LATEST SCORES:")
            for category, score in scores.items():
                status_icon = "✅" if score >= 30 else "❌"
                print(f"   {status_icon} {category}: {score:.2f}")
        
        print(f"{'='*60}")
    
    def run_monitoring(self):
        """Run continuous monitoring"""
        print("👁️ REAL-TIME OPTIMIZER MONITORING STARTED")
        print(f"🔄 Checking every {self.check_interval} seconds")
        print("📊 Press Ctrl+C to stop monitoring\n")
        
        try:
            iteration = 0
            while True:
                iteration += 1
                self.print_status_update()
                
                # Check if process is still running
                if not self.get_process_status()['running']:
                    print("\n⚠️  OPTIMIZER STOPPED - Checking completion status...")
                    
                    # Check logs for completion or error
                    logs = self.get_latest_logs(20)
                    log_text = ' '.join(logs)
                    
                    if 'MISSION ACCOMPLISHED' in log_text:
                        print("🎉 OPTIMIZATION COMPLETED SUCCESSFULLY!")
                        print("🎊 All categories should be above 30 and submitted to grade API!")
                        break
                    elif 'ERROR' in log_text or 'FAILED' in log_text:
                        print("❌ OPTIMIZER ENCOUNTERED AN ERROR")
                        print("📋 Check logs for details")
                        break
                    else:
                        print("ℹ️  Optimizer stopped - reason unclear")
                        break
                
                # Wait for next check
                print(f"\n⏳ Next check in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 MONITORING STOPPED BY USER")
            print("📊 Final status check...")
            self.print_status_update()
            
            # Show how to resume monitoring
            print(f"\n💡 To resume monitoring, run:")
            print(f"   python monitor_final_optimizer.py")

if __name__ == "__main__":
    monitor = OptimizerMonitor()
    monitor.run_monitoring() 