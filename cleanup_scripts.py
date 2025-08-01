#!/usr/bin/env python3
"""
🧹 CODEBASE CLEANUP SCRIPT
========================
Removes experimental scripts and organizes the final codebase.
"""

import os
import shutil
from datetime import datetime

def cleanup_experimental_scripts():
    """Remove all experimental optimization scripts"""
    scripts_to_remove = [
        "iterative_improvement.py",
        "focused_improvement.py", 
        "emergency_recovery.py",
        "patient_final_push.py",
        "rate_limit_aware_script.py",
        "final_two_categories.py",
        "final_grade_submission.py",
        "grade_api_submission.py",
        "submit_biology_grade.py",
        "improve_doctors_quant.py",
        "fast_improvement_no_limits.py",
        "submit_individual_grades.py",
        "submit_correct_format.py",
        "complete_final_submission.py",
        "submit_all_categories_final.py",
        "optimize_below_30.py",
        "targeted_optimization_script.py",
        "final_three_categories_fix.py"
    ]
    
    # Create archive directory
    archive_dir = "archived_experiments"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    
    removed_count = 0
    
    for script in scripts_to_remove:
        if os.path.exists(script):
            try:
                # Move to archive instead of deleting
                shutil.move(script, f"{archive_dir}/{script}")
                print(f"📦 Archived: {script}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error archiving {script}: {e}")
    
    print(f"\n✅ Archived {removed_count} experimental scripts")
    
def cleanup_progress_files():
    """Organize progress files"""
    progress_files = [
        "iterative_progress.json",
        "focused_progress.json", 
        "comprehensive_final_results.json"
    ]
    
    archive_dir = "archived_progress"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        
    for file in progress_files:
        if os.path.exists(file):
            try:
                shutil.move(file, f"{archive_dir}/{file}")
                print(f"📊 Archived progress file: {file}")
            except Exception as e:
                print(f"❌ Error archiving {file}: {e}")

def create_final_structure():
    """Create clean final project structure"""
    
    # Ensure logs directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    # Ensure results directory exists
    if not os.path.exists("results"):
        os.makedirs("results")
        
    print("📁 Verified final directory structure")

if __name__ == "__main__":
    print("🧹 CLEANING UP CODEBASE")
    print("=" * 50)
    
    cleanup_experimental_scripts()
    cleanup_progress_files() 
    create_final_structure()
    
    print("\n🎉 CODEBASE CLEANUP COMPLETE!")
    print("📋 Final structure:")
    print("  - comprehensive_automated_optimizer.py (MAIN SCRIPT)")
    print("  - src/ (core modules)")
    print("  - logs/ (optimization logs)")
    print("  - results/ (evaluation results)")
    print("  - archived_experiments/ (old scripts)")
    print("  - archived_progress/ (old progress files)") 