#!/usr/bin/env python3
"""
Progress Monitor for Focused Improvement
========================================
Real-time monitoring of category scores and progress.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def monitor_progress():
    """Monitor current progress and identify remaining work."""
    target_score = 30.0
    
    print("🔍 PROGRESS MONITOR")
    print("=" * 50)
    print(f"🎯 Target: ALL categories >= {target_score}")
    print("=" * 50)
    
    # Check for progress files
    progress_files = [
        "results/focused_progress.json",
        "results/iterative_progress.json", 
        "results/final_submission_20250801_170057.json"
    ]
    
    latest_scores = {}
    
    for file_path in progress_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Extract scores from different file formats
                if "current_scores" in data:
                    latest_scores = data["current_scores"]
                    print(f"📊 Found scores in {file_path}")
                    break
                elif "scores" in data:
                    latest_scores = data["scores"]
                    print(f"📊 Found scores in {file_path}")
                    break
                elif "api_submission_results" in data:
                    api_results = data["api_submission_results"]
                    if "final_grades" in api_results:
                        for cat, grade in api_results["final_grades"].items():
                            latest_scores[cat] = grade["score"]
                        print(f"📊 Found scores in {file_path}")
                        break
            except Exception as e:
                continue
    
    if not latest_scores:
        print("❌ No current scores found. Script may still be getting initial scores.")
        return
    
    # Analyze current status
    problems = []
    passing = []
    
    for category, score in latest_scores.items():
        if score < target_score:
            deficit = target_score - score
            problems.append((category, score, deficit))
        else:
            passing.append((category, score))
    
    # Sort problems by deficit (worst first)
    problems.sort(key=lambda x: x[2], reverse=True)
    passing.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n✅ PASSING CATEGORIES ({len(passing)}/10):")
    print("-" * 40)
    for category, score in passing:
        surplus = score - target_score
        print(f"✅ {category:<35}: {score:>8.2f} (+{surplus:.2f})")
    
    print(f"\n❌ NEED IMPROVEMENT ({len(problems)}/10):")
    print("-" * 40)
    for category, score, deficit in problems:
        print(f"❌ {category:<35}: {score:>8.2f} (needs +{deficit:.2f})")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Categories above {target_score}: {len(passing)}")
    print(f"❌ Categories below {target_score}: {len(problems)}")
    print(f"📈 Success rate: {len(passing)/len(latest_scores)*100:.1f}%")
    
    if len(problems) == 0:
        print("\n🎉 SUCCESS! ALL CATEGORIES ABOVE TARGET!")
        return True
    else:
        print(f"\n🎯 NEXT PRIORITY: Focus on {problems[0][0]} (deficit: -{problems[0][2]:.2f})")
        return False

def check_script_status():
    """Check if the focused improvement script is still running."""
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'focused_improvement.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pid = result.stdout.strip()
            print(f"✅ Focused improvement script is running (PID: {pid})")
            return True
        else:
            print("❌ Focused improvement script is not running")
            return False
    except:
        print("⚠️ Could not check script status")
        return False

def suggest_next_actions(all_above_target: bool, script_running: bool):
    """Suggest next actions based on current status."""
    print("\n🔧 SUGGESTED NEXT ACTIONS:")
    print("-" * 30)
    
    if all_above_target:
        print("🎉 1. All categories above target - MISSION ACCOMPLISHED!")
        print("📊 2. Run final evaluation to confirm scores")
        print("📋 3. Generate final submission report")
    elif script_running:
        print("⏳ 1. Script is actively working - let it continue")
        print("👀 2. Monitor progress every few minutes")
        print("🔧 3. Script will focus on most problematic categories")
    else:
        print("🚀 1. Restart focused improvement script")
        print("🎯 2. Focus on categories with largest deficits")
        print("🔧 3. Try alternative search strategies")

if __name__ == "__main__":
    try:
        all_above_target = monitor_progress()
        script_running = check_script_status()
        suggest_next_actions(all_above_target, script_running)
        
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring interrupted")
    except Exception as e:
        print(f"❌ Error: {e}") 