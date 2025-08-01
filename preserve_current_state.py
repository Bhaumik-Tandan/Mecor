#!/usr/bin/env python3
"""
Preserve Current State
=====================
Document current achievements without API calls.
Prepare for emergency recovery phase.
"""

import json
import time
from pathlib import Path
from datetime import datetime

def preserve_current_state():
    """Preserve current state and document achievements."""
    
    print("🛡️ PRESERVING CURRENT STATE")
    print("=" * 50)
    print("📄 Reading from all available result files...")
    print("⚠️  NO API CALLS - preserving what we have")
    print("=" * 50)
    
    # Collect all available scores
    all_scores = {}
    
    # Read from focused_progress.json (latest from monitor)
    focused_progress_file = "results/focused_progress.json"
    if Path(focused_progress_file).exists():
        try:
            with open(focused_progress_file, 'r') as f:
                data = json.load(f)
            if "current_scores" in data:
                all_scores.update(data["current_scores"])
                print(f"📊 Read scores from {focused_progress_file}")
        except Exception as e:
            print(f"⚠️ Could not read {focused_progress_file}: {e}")
    
    # Check logs for biology_expert.yml success (line 102-104)
    biology_success = False
    try:
        with open("logs/focused_improvement.log", 'r') as f:
            log_content = f.read()
        
        if "biology_expert.yml: Improved to 32.00" in log_content and "REACHED TARGET" in log_content:
            all_scores["biology_expert.yml"] = 32.00
            biology_success = True
            print("🎉 Found biology_expert.yml SUCCESS in logs: 32.00!")
    except:
        pass
    
    # Document current state
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    preserved_state = {
        "timestamp": timestamp,
        "preservation_reason": "Rate limit crisis - preserving before emergency recovery",
        "current_scores": all_scores,
        "achievements_found": {
            "biology_expert_success": biology_success,
            "total_categories_found": len(all_scores)
        },
        "analysis": {
            "passing_categories": [],
            "failing_categories": [],
            "total_passing": 0,
            "success_rate": 0.0
        }
    }
    
    # Analyze scores
    target = 30.0
    for category, score in all_scores.items():
        if score >= target:
            preserved_state["analysis"]["passing_categories"].append({
                "category": category,
                "score": score,
                "surplus": score - target
            })
        else:
            preserved_state["analysis"]["failing_categories"].append({
                "category": category,
                "score": score,
                "deficit": target - score
            })
    
    preserved_state["analysis"]["total_passing"] = len(preserved_state["analysis"]["passing_categories"])
    preserved_state["analysis"]["success_rate"] = len(preserved_state["analysis"]["passing_categories"]) / 10 * 100
    
    # Save preserved state
    preserve_file = f"results/preserved_state_{timestamp}.json"
    with open(preserve_file, 'w') as f:
        json.dump(preserved_state, f, indent=2)
    
    print(f"\n✅ STATE PRESERVED: {preserve_file}")
    print("\n📊 PRESERVED STATE ANALYSIS:")
    print("=" * 50)
    
    print(f"✅ PASSING CATEGORIES ({preserved_state['analysis']['total_passing']}/10):")
    for cat in preserved_state["analysis"]["passing_categories"]:
        print(f"   ✅ {cat['category']}: {cat['score']:.2f} (+{cat['surplus']:.2f})")
    
    print(f"\n❌ FAILING CATEGORIES ({len(preserved_state['analysis']['failing_categories'])}/10):")
    for cat in preserved_state["analysis"]["failing_categories"]:
        print(f"   ❌ {cat['category']}: {cat['score']:.2f} (needs +{cat['deficit']:.2f})")
    
    print(f"\n📈 SUCCESS RATE: {preserved_state['analysis']['success_rate']:.1f}%")
    
    if biology_success:
        print(f"\n🎉 CONFIRMED: biology_expert.yml reached 32.00 (found in logs)")
        print("📊 Actual success rate may be higher than file records show")
    
    print("\n🛡️ CURRENT STATE SAFELY PRESERVED")
    print("🚀 Ready for emergency recovery phase")
    
    return preserved_state

if __name__ == "__main__":
    preserve_current_state() 