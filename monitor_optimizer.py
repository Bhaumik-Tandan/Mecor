#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE OPTIMIZER MONITOR
=================================
Real-time monitoring dashboard for the automated optimization system.
"""

import os
import time
import json
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

class OptimizerMonitor:
    def __init__(self):
        self.log_file = "logs/comprehensive_optimizer.log"
        self.progress_file = "comprehensive_progress.json"
        self.target_categories = [
            "tax_lawyer.yml",
            "anthropology.yml", 
            "biology_expert.yml",
            "quantitative_finance.yml",
            "doctors_md.yml",
            "junior_corporate_lawyer.yml"
        ]
        
    def get_process_status(self):
        """Get comprehensive optimizer process status"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'comprehensive_automated_optimizer.py' in line and 'grep' not in line:
                    parts = line.split()
                    if len(parts) >= 11:
                        return {
                            'pid': parts[1],
                            'cpu_percent': parts[2],
                            'memory_percent': parts[3],
                            'memory_mb': f"{float(parts[5]) / 1024:.1f}MB" if parts[5].isdigit() else parts[5],
                            'status': parts[7],
                            'runtime': parts[9],
                            'is_running': True
                        }
            return {'is_running': False}
        except Exception as e:
            return {'error': str(e), 'is_running': False}
    
    def get_recent_logs(self, lines=20):
        """Get recent log entries"""
        try:
            if os.path.exists(self.log_file):
                result = subprocess.run(['tail', f'-{lines}', self.log_file], 
                                      capture_output=True, text=True)
                return result.stdout.strip().split('\n')
            return ["Log file not found"]
        except Exception as e:
            return [f"Error reading logs: {e}"]
    
    def get_log_stats(self):
        """Get log file statistics"""
        try:
            if os.path.exists(self.log_file):
                stat = os.stat(self.log_file)
                return {
                    'size_mb': f"{stat.st_size / (1024*1024):.1f}MB",
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%H:%M:%S'),
                    'lines': int(subprocess.run(['wc', '-l', self.log_file], 
                                              capture_output=True, text=True).stdout.split()[0])
                }
            return {'size_mb': '0MB', 'modified': 'Never', 'lines': 0}
        except Exception as e:
            return {'error': str(e)}
    
    def get_current_progress(self):
        """Get current optimization progress"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_resources(self):
        """Get system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': f"{cpu_percent:.1f}%",
                'memory_percent': f"{memory.percent:.1f}%",
                'memory_available': f"{memory.available / (1024**3):.1f}GB",
                'disk_free': f"{disk.free / (1024**3):.1f}GB"
            }
        except Exception as e:
            return {'error': str(e)}
    
    def count_recent_api_calls(self, minutes=10):
        """Count API calls in recent logs"""
        try:
            if not os.path.exists(self.log_file):
                return 0
                
            # Get logs from last N minutes
            result = subprocess.run(['tail', '-1000', self.log_file], 
                                  capture_output=True, text=True)
            
            count = 0
            current_time = datetime.now()
            
            for line in result.stdout.split('\n'):
                if 'HTTP Request:' in line and 'turbopuffer' in line:
                    try:
                        # Extract timestamp
                        if '|' in line:
                            timestamp_str = line.split('|')[0].strip()
                            log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                            
                            # Check if within last N minutes
                            time_diff = (current_time - log_time).total_seconds() / 60
                            if time_diff <= minutes:
                                count += 1
                    except:
                        continue
                        
            return count
        except Exception as e:
            return f"Error: {e}"
    
    def extract_latest_scores(self):
        """Extract latest scores from logs"""
        try:
            if not os.path.exists(self.log_file):
                return {}
                
            result = subprocess.run(['tail', '-500', self.log_file], 
                                  capture_output=True, text=True)
            
            scores = {}
            for line in reversed(result.stdout.split('\n')):
                if 'Safe evaluation completed for' in line and ': ' in line:
                    try:
                        # Extract category and score
                        parts = line.split('Safe evaluation completed for')[1]
                        category = parts.split(':')[0].strip()
                        score_part = parts.split(':')[1].strip()
                        score = float(score_part.split()[0])
                        
                        if category not in scores:  # Only take most recent
                            scores[category] = score
                    except:
                        continue
                        
            return scores
        except Exception as e:
            return {'error': str(e)}
    
    def display_dashboard(self):
        """Display comprehensive monitoring dashboard"""
        os.system('clear')
        
        print("🔍 " + "="*80)
        print("🚀 COMPREHENSIVE OPTIMIZER MONITOR - LIVE DASHBOARD")
        print("="*82)
        print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Process Status
        process_status = self.get_process_status()
        if process_status.get('is_running'):
            print("📊 PROCESS STATUS: ✅ RUNNING")
            print(f"   PID: {process_status['pid']}")
            print(f"   CPU: {process_status['cpu_percent']}%")
            print(f"   Memory: {process_status['memory_percent']}% ({process_status['memory_mb']})")
            print(f"   Status: {process_status['status']}")
            print(f"   Runtime: {process_status['runtime']}")
        else:
            print("📊 PROCESS STATUS: ❌ NOT RUNNING")
            if 'error' in process_status:
                print(f"   Error: {process_status['error']}")
        print()
        
        # Log Statistics
        log_stats = self.get_log_stats()
        print("📝 LOG FILE STATUS:")
        if 'error' not in log_stats:
            print(f"   Size: {log_stats['size_mb']}")
            print(f"   Lines: {log_stats['lines']:,}")
            print(f"   Last Modified: {log_stats['modified']}")
        else:
            print(f"   Error: {log_stats['error']}")
        print()
        
        # API Activity
        api_calls = self.count_recent_api_calls(10)
        print(f"🌐 API ACTIVITY (Last 10 min): {api_calls} calls")
        print()
        
        # Latest Scores
        latest_scores = self.extract_latest_scores()
        print("🎯 LATEST SCORES:")
        if latest_scores and 'error' not in latest_scores:
            for category in self.target_categories:
                if category in latest_scores:
                    score = latest_scores[category]
                    status = "✅" if score >= 30 else "🔄"
                    print(f"   {status} {category:<25} {score:>6.2f}")
                else:
                    print(f"   ⏳ {category:<25} {'--':>6}")
        else:
            print("   No scores available yet")
        print()
        
        # Progress File
        progress = self.get_current_progress()
        if progress and 'error' not in progress:
            print("📈 PROGRESS FILE:")
            print(f"   Timestamp: {progress.get('timestamp', 'Unknown')}")
            print(f"   Submitted: {len(progress.get('submitted_categories', []))}/6")
            print(f"   Target Score: {progress.get('target_score', 30)}")
        else:
            print("📈 PROGRESS FILE: Not available")
        print()
        
        # System Resources
        resources = self.get_system_resources()
        print("💻 SYSTEM RESOURCES:")
        if 'error' not in resources:
            print(f"   CPU Usage: {resources['cpu_percent']}")
            print(f"   Memory Usage: {resources['memory_percent']} ({resources['memory_available']} available)")
            print(f"   Disk Free: {resources['disk_free']}")
        else:
            print(f"   Error: {resources['error']}")
        print()
        
        # Recent Log Lines
        print("📋 RECENT ACTIVITY (Last 10 lines):")
        recent_logs = self.get_recent_logs(10)
        for line in recent_logs[-10:]:
            if line.strip():
                # Highlight important events
                if any(keyword in line for keyword in ['✅', '🎉', '🏆', 'SUCCESS', 'completed']):
                    print(f"   🟢 {line}")
                elif any(keyword in line for keyword in ['❌', 'ERROR', 'Failed']):
                    print(f"   🔴 {line}")
                elif 'INFO' in line:
                    print(f"   ⚪ {line}")
                else:
                    print(f"   ⚫ {line}")
        
        print()
        print("="*82)
        print("🔄 Refreshing every 5 seconds... Press Ctrl+C to stop monitoring")
        print("="*82)
    
    def run_continuous_monitor(self):
        """Run continuous monitoring dashboard"""
        try:
            while True:
                self.display_dashboard()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
            print("✅ Optimizer continues running in background")

if __name__ == "__main__":
    monitor = OptimizerMonitor()
    monitor.run_continuous_monitor() 