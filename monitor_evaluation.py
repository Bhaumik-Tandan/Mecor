#!/usr/bin/env python3
"""
Evaluation Monitor
=================

Monitor the progress of the automated evaluation system.
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime
import glob

def monitor_evaluation():
    """Monitor the evaluation progress."""
    print("🔍 Evaluation Monitor")
    print("=" * 40)
    
    while True:
        try:
            # Check if evaluation is running
            evaluation_running = check_evaluation_status()
            
            if evaluation_running:
                print(f"✅ Evaluation is running - {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"❌ Evaluation not running - {datetime.now().strftime('%H:%M:%S')}")
            
            # Show progress
            show_progress()
            
            # Show recent results
            show_recent_results()
            
            # Show improvements
            show_improvements()
            
            print("-" * 40)
            time.sleep(30)  # Update every 30 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            time.sleep(60)

def check_evaluation_status():
    """Check if evaluation is running."""
    try:
        # Check for robust_auto_eval.py process
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'robust_auto_eval.py'], capture_output=True)
        return result.returncode == 0
    except:
        return False

def show_progress():
    """Show evaluation progress."""
    try:
        # Count evaluation reports
        reports = glob.glob("evaluation_reports/progress_*.json")
        if reports:
            latest_report = max(reports, key=os.path.getctime)
            
            with open(latest_report, 'r') as f:
                data = json.load(f)
            
            print(f"📊 Progress: Cycle {data.get('cycle_count', 0)}")
            print(f"📈 Total Evaluations: {data.get('total_evaluations', 0)}")
            print(f"🔧 Improvements: {data.get('total_improvements', 0)}")
        else:
            print("📊 No progress reports found")
    except Exception as e:
        print(f"❌ Error reading progress: {e}")

def show_recent_results():
    """Show recent evaluation results."""
    try:
        # Find latest progress report
        reports = glob.glob("evaluation_reports/progress_*.json")
        if reports:
            latest_report = max(reports, key=os.path.getctime)
            
            with open(latest_report, 'r') as f:
                data = json.load(f)
            
            recent_results = data.get('recent_results', [])
            if recent_results:
                print(f"🎯 Recent Results ({len(recent_results)}):")
                for result in recent_results[-3:]:  # Show last 3
                    query = result.get('query', 'Unknown')
                    gpt_score = result.get('gpt_evaluation_score', 0)
                    candidates = result.get('candidate_count', 0)
                    print(f"  • {query}: {candidates} candidates, GPT score: {gpt_score:.2f}")
    except Exception as e:
        print(f"❌ Error reading results: {e}")

def show_improvements():
    """Show recent improvements."""
    try:
        # Find latest progress report
        reports = glob.glob("evaluation_reports/progress_*.json")
        if reports:
            latest_report = max(reports, key=os.path.getctime)
            
            with open(latest_report, 'r') as f:
                data = json.load(f)
            
            improvements = data.get('recent_improvements', [])
            if improvements:
                print(f"🔧 Recent Improvements ({len(improvements)}):")
                for imp in improvements[-2:]:  # Show last 2
                    improvement = imp.get('improvement', 'Unknown')
                    print(f"  • {improvement}")
    except Exception as e:
        print(f"❌ Error reading improvements: {e}")

def show_logs():
    """Show recent log entries."""
    try:
        log_file = "logs/robust_auto_eval.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    print("📝 Recent Logs:")
                    for line in lines[-5:]:  # Show last 5 lines
                        print(f"  {line.strip()}")
    except Exception as e:
        print(f"❌ Error reading logs: {e}")

if __name__ == "__main__":
    monitor_evaluation() 