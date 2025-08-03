#!/usr/bin/env python3
"""
👁️ DEADLINE OPTIMIZER MONITOR
=============================
Monitor the continuous optimizer until deadline
"""

import os
import time
import json
import glob
from datetime import datetime, timedelta

def monitor_optimizer():
    """Monitor the continuous optimizer progress"""
    print("👁️ DEADLINE OPTIMIZER MONITOR")
    print("=" * 50)
    print(f"🕐 Started monitoring at: {datetime.now().strftime('%H:%M:%S')}")
    print("📊 Tracking progress until 11 PM PST deadline...")
    print("")
    
    last_log_size = 0
    iteration_count = 0
    
    while True:
        # Check for latest log file
        log_files = glob.glob("logs/continuous_optimizer_*.log")
        if log_files:
            latest_log = max(log_files, key=os.path.getctime)
            
            # Check if log file grew (new activity)
            current_size = os.path.getsize(latest_log)
            if current_size > last_log_size:
                print(f"📈 Log activity detected: {latest_log}")
                
                # Read recent lines
                with open(latest_log, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-10:]  # Last 10 lines
                    
                    for line in recent_lines:
                        if any(keyword in line for keyword in ['IMPROVEMENT', 'MILESTONE', 'SUCCESS', 'SUBMITTING']):
                            print(f"🎉 {line.strip()}")
                        elif 'ITERATION' in line:
                            print(f"🔄 {line.strip()}")
                
                last_log_size = current_size
        
        # Check for improved submission files
        submission_files = glob.glob("improved_submission_*_of_10.json")
        if submission_files:
            latest_submission = max(submission_files, key=os.path.getctime)
            
            try:
                with open(latest_submission, 'r') as f:
                    data = json.load(f)
                    above_30 = data.get('categories_above_30', 0)
                    iteration = data.get('iteration', 0)
                    
                    if iteration > iteration_count:
                        print(f"📤 Latest submission: {above_30}/10 categories above 30")
                        print(f"🔄 Iteration: {iteration}")
                        iteration_count = iteration
            except:
                pass
        
        # Status update
        current_time = datetime.now()
        print(f"⏰ {current_time.strftime('%H:%M:%S')} - Monitoring active...")
        
        # Wait before next check
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        monitor_optimizer()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Monitor error: {e}") 