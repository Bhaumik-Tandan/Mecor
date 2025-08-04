#!/usr/bin/env python3
"""
3-Hour Evaluation Monitor
========================

Monitor the robust evaluation system running for 3 hours with all improvements.
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime
import glob

def monitor_3hour_evaluation():
    """Monitor the 3-hour evaluation progress."""
    print("🔍 3-Hour Evaluation Monitor")
    print("=" * 50)
    print("Monitoring robust evaluation with all improvements:")
    print("✅ Filter extraction enhancement")
    print("✅ GPT prompt optimization")
    print("✅ Search algorithm optimization")
    print("✅ Multi-threaded processing")
    print("✅ Continuous improvement system")
    print()
    
    start_time = time.time()
    end_time = start_time + (3 * 60 * 60)  # 3 hours
    
    while time.time() < end_time:
        try:
            current_time = datetime.now()
            elapsed = time.time() - start_time
            remaining = end_time - time.time()
            
            print(f"⏰ {current_time.strftime('%H:%M:%S')} - Elapsed: {elapsed/60:.1f}min, Remaining: {remaining/60:.1f}min")
            
            # Check if evaluation is running
            evaluation_running = check_evaluation_status()
            
            if evaluation_running:
                print(f"✅ Evaluation is running - {current_time.strftime('%H:%M:%S')}")
            else:
                print(f"❌ Evaluation not running - {current_time.strftime('%H:%M:%S')}")
            
            # Show progress
            show_progress()
            
            # Show recent results
            show_recent_results()
            
            # Show improvements
            show_improvements()
            
            # Show filter extraction activity
            show_filter_extraction_activity()
            
            print("-" * 50)
            time.sleep(60)  # Update every minute
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            time.sleep(60)
    
    print("\n🎉 3-hour evaluation monitoring completed!")

def check_evaluation_status():
    """Check if evaluation is running."""
    try:
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

def show_filter_extraction_activity():
    """Show filter extraction activity."""
    try:
        # Check for filter extraction in logs
        log_file = "logs/robust_auto_eval.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    # Look for filter extraction activity
                    filter_lines = [line for line in lines[-20:] if 'filter' in line.lower() or 'enhanced' in line.lower()]
                    if filter_lines:
                        print(f"🔍 Filter Activity: {len(filter_lines)} recent filter-related operations")
                    else:
                        print("🔍 Filter Activity: Normal operation")
    except Exception as e:
        print(f"❌ Error reading filter activity: {e}")

def show_performance_metrics():
    """Show performance metrics."""
    try:
        # Find latest progress report
        reports = glob.glob("evaluation_reports/progress_*.json")
        if reports:
            latest_report = max(reports, key=os.path.getctime)
            
            with open(latest_report, 'r') as f:
                data = json.load(f)
            
            recent_results = data.get('recent_results', [])
            if recent_results:
                avg_response_time = sum(r.get('response_time', 0) for r in recent_results) / len(recent_results)
                avg_gpt_score = sum(r.get('gpt_evaluation_score', 0) for r in recent_results) / len(recent_results)
                avg_quality = sum(r.get('quality_score', 0) for r in recent_results) / len(recent_results)
                
                print(f"📊 Performance: Response: {avg_response_time:.2f}s, GPT: {avg_gpt_score:.2f}, Quality: {avg_quality:.2f}")
    except Exception as e:
        print(f"❌ Error reading performance: {e}")

if __name__ == "__main__":
    monitor_3hour_evaluation() 