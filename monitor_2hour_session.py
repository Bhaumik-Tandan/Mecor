#!/usr/bin/env python3
"""
📊 2-HOUR ULTRA-ROBUST SESSION MONITOR
====================================
Real-time monitoring for the 2-hour optimization session.
"""

import os
import time
import json
import subprocess
from datetime import datetime, timedelta

def monitor_session():
    """Monitor the 2-hour ultra-robust optimization session"""
    
    print("📊 2-HOUR ULTRA-ROBUST SESSION MONITOR")
    print("="*50)
    
    while True:
        os.system('clear')
        
        print("🔥 ULTRA-ROBUST 2-HOUR OPTIMIZATION SESSION")
        print("="*60)
        print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check process status
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'ultra_robust_optimizer.py' in result.stdout:
                lines = [line for line in result.stdout.split('\n') if 'ultra_robust_optimizer.py' in line and 'grep' not in line]
                if lines:
                    parts = lines[0].split()
                    print("📊 PROCESS STATUS: ✅ RUNNING")
                    print(f"   PID: {parts[1]}")
                    print(f"   CPU: {parts[2]}%")
                    print(f"   Memory: {parts[3]}%")
                    print(f"   Runtime: {parts[9]}")
            else:
                print("📊 PROCESS STATUS: ❌ NOT RUNNING")
        except:
            print("📊 PROCESS STATUS: ❓ UNKNOWN")
        
        print()
        
        # Check latest logs
        log_files = []
        try:
            for f in os.listdir('logs'):
                if f.startswith('ultra_robust_2025'):
                    log_files.append(f)
            
            if log_files:
                latest_log = sorted(log_files)[-1]
                print(f"📝 LATEST LOG: {latest_log}")
                
                # Get recent activity
                try:
                    result = subprocess.run(['tail', '-10', f'logs/{latest_log}'], capture_output=True, text=True)
                    recent_lines = result.stdout.strip().split('\n')[-5:]
                    
                    print("🌐 RECENT ACTIVITY:")
                    for line in recent_lines:
                        if line.strip():
                            # Color code by importance
                            if any(word in line.upper() for word in ['ERROR', 'FAILED']):
                                print(f"   🔴 {line}")
                            elif any(word in line.upper() for word in ['SUCCESS', 'COMPLETED', 'SUBMITTED']):
                                print(f"   🟢 {line}")
                            elif 'INFO' in line:
                                print(f"   ⚪ {line}")
                            else:
                                print(f"   ⚫ {line}")
                except:
                    print("   📋 Log reading error")
        except:
            print("📝 LOGS: Not accessible")
        
        print()
        
        # Check progress file
        try:
            if os.path.exists('ultra_robust_progress.json'):
                with open('ultra_robust_progress.json', 'r') as f:
                    progress = json.load(f)
                
                print("📈 PROGRESS STATUS:")
                print(f"   ✅ Submitted: {len(progress.get('submitted_categories', []))}/6")
                print(f"   ⏰ Runtime: {progress.get('runtime_hours', 0):.2f} hours")
                print(f"   🎯 Target: {progress.get('target_duration_hours', 2.17):.2f} hours")
                
                submitted = progress.get('submitted_categories', [])
                if submitted:
                    print(f"   🏆 Completed: {', '.join(submitted)}")
        except:
            print("📈 PROGRESS: No data available")
        
        print()
        
        # Check system resources
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print("💻 SYSTEM RESOURCES:")
            print(f"   CPU: {cpu:.1f}%")
            print(f"   Memory: {memory.percent:.1f}% ({memory.available/(1024**3):.1f}GB free)")
            print(f"   Disk: {disk.free/(1024**3):.1f}GB free")
        except:
            print("💻 SYSTEM: Resource data unavailable")
        
        print()
        print("="*60)
        print("🔄 Refreshing every 30 seconds... Press Ctrl+C to stop")
        print("✅ Optimizer continues running independently")
        print("="*60)
        
        time.sleep(30)

if __name__ == "__main__":
    try:
        monitor_session()
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")
        print("✅ Ultra-robust optimizer continues running in background") 