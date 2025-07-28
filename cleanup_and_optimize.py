#!/usr/bin/env python3
"""
Project Cleanup and Optimization Tool
=====================================

Simplified tool to clean up project structure and generate final submission.
"""

import os
import shutil
import glob
import json
import time
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Set

class SimpleProjectCleaner:
    """Simple project cleaner without complex dependencies."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
    def clean_useless_files(self) -> Dict[str, int]:
        """Remove useless files from the project."""
        
        useless_patterns = [
            # Old script versions
            "search_agent*.py",
            "test_script*.py", 
            "*_improved.py",
            "*_final.py",
            "*_optimized.py",
            "*_enhanced.py",
            
            # Test files
            "test_soft_filters.py",
            "test_domain_validation.py",
            
            # Documentation files (keeping only README.md)
            "README_IMPROVEMENTS.md",
            "PROJECT_STRUCTURE.md",
            "AI_ORCHESTRATOR_REPORT.md",
            
            # Intermediate submission files
            "submission_format_example.json",
            "generate_submission.py",  # Keep only create_final_submission.py
            
            # Log files
            "*.log",
            "logs/",
            
            # Cache files
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
        ]
        
        files_removed = 0
        space_saved = 0
        
        print("🧹 CLEANING USELESS FILES")
        print("=" * 40)
        
        for pattern in useless_patterns:
            matches = list(self.project_root.glob(pattern))
            for file_path in matches:
                if file_path.exists():
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        print(f"  ❌ Removing: {file_path.name} ({size/1024:.1f}KB)")
                        file_path.unlink()
                        files_removed += 1
                        space_saved += size
                    elif file_path.is_dir():
                        print(f"  ❌ Removing directory: {file_path.name}/")
                        shutil.rmtree(file_path)
                        files_removed += 1
        
        print(f"\n📊 Cleanup completed:")
        print(f"  Files/directories removed: {files_removed}")
        print(f"  Space saved: {space_saved/1024:.1f}KB")
        
        return {
            "files_removed": files_removed,
            "space_saved_kb": space_saved / 1024
        }
    
    def organize_structure(self) -> bool:
        """Ensure proper project structure."""
        
        print("\n🏗️ ORGANIZING PROJECT STRUCTURE")
        print("=" * 40)
        
        # Ensure essential directories exist
        essential_dirs = [
            "src/config",
            "src/models", 
            "src/services",
            "src/agents",
            "src/utils"
        ]
        
        for dir_path in essential_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                print(f"📁 Creating directory: {dir_path}")
                full_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ Project structure organized")
        return True

def test_search_quality() -> Dict[str, float]:
    """Test search quality with a simple check."""
    
    print("\n🧪 TESTING SEARCH QUALITY")
    print("=" * 40)
    
    try:
        # Simple test: run a vector search for mathematics
        sys.path.insert(0, 'src')
        from src.services.search_service import search_service
        from src.models.candidate import SearchQuery, SearchStrategy
        
        query = SearchQuery(
            query_text="mathematics professor PhD research",
            job_category="mathematics_phd.yml",
            strategy=SearchStrategy.VECTOR_ONLY,
            max_candidates=5
        )
        
        candidates = search_service.vector_search(query.query_text, 5)
        
        print(f"✅ Vector search test: Found {len(candidates)} candidates")
        
        # Check if we found actual mathematicians
        math_keywords = ["mathematics", "mathematical", "math", "professor", "PhD"]
        relevant_candidates = 0
        
        for candidate in candidates:
            summary_lower = (candidate.summary or "").lower()
            if any(keyword.lower() in summary_lower for keyword in math_keywords):
                relevant_candidates += 1
                print(f"  📝 {candidate.name}: Relevant mathematics candidate")
        
        relevance_score = relevant_candidates / len(candidates) if candidates else 0
        print(f"📊 Relevance score: {relevance_score:.2f}")
        
        return {
            "candidates_found": len(candidates),
            "relevant_candidates": relevant_candidates,
            "relevance_score": relevance_score
        }
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return {
            "candidates_found": 0,
            "relevant_candidates": 0,
            "relevance_score": 0.0,
            "error": str(e)
        }

def generate_final_submission() -> Dict[str, any]:
    """Generate the final submission."""
    
    print("\n🎯 GENERATING FINAL SUBMISSION")
    print("=" * 40)
    
    try:
        # Run the submission generator
        result = subprocess.run([
            sys.executable, "create_final_submission.py"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Final submission generated successfully")
            
            # Check if submission file exists
            submission_file = Path("final_submission.json")
            if submission_file.exists():
                with open(submission_file, 'r') as f:
                    submission_data = json.load(f)
                
                categories = len(submission_data.get("config_candidates", {}))
                total_candidates = sum(len(candidates) for candidates in submission_data.get("config_candidates", {}).values())
                
                print(f"📊 Submission Statistics:")
                print(f"  Categories: {categories}")
                print(f"  Total Candidates: {total_candidates}")
                print(f"  File Size: {submission_file.stat().st_size / 1024:.1f}KB")
                
                return {
                    "success": True,
                    "categories": categories,
                    "total_candidates": total_candidates,
                    "file_size_kb": submission_file.stat().st_size / 1024
                }
            else:
                return {"success": False, "error": "Submission file not created"}
        else:
            print(f"❌ Submission generation failed:")
            print(result.stderr)
            return {"success": False, "error": result.stderr}
            
    except Exception as e:
        print(f"❌ Submission generation failed: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Main optimization process."""
    
    print("🚀 PROJECT OPTIMIZATION AND CLEANUP")
    print("=" * 80)
    print("Automated cleanup, testing, and submission generation")
    print()
    
    start_time = time.time()
    
    # Step 1: Clean up project
    cleaner = SimpleProjectCleaner()
    cleanup_stats = cleaner.clean_useless_files()
    cleaner.organize_structure()
    
    # Step 2: Test search quality
    search_quality = test_search_quality()
    
    # Step 3: Generate submission
    submission_result = generate_final_submission()
    
    # Step 4: Final assessment
    duration = time.time() - start_time
    
    print(f"\n🎉 OPTIMIZATION COMPLETE!")
    print("=" * 40)
    print(f"Duration: {duration:.1f}s")
    print(f"Files cleaned: {cleanup_stats['files_removed']}")
    print(f"Space saved: {cleanup_stats['space_saved_kb']:.1f}KB")
    
    if search_quality.get("relevance_score", 0) >= 0.5:
        print("✅ Search quality: Good")
    else:
        print("⚠️ Search quality: Needs improvement")
    
    if submission_result.get("success"):
        print("✅ Submission: Generated successfully")
        print(f"   Categories: {submission_result['categories']}")
        print(f"   Candidates: {submission_result['total_candidates']}")
    else:
        print("❌ Submission: Failed to generate")
    
    # Final grade
    score = 0
    if cleanup_stats['files_removed'] > 0:
        score += 0.3
    if search_quality.get("relevance_score", 0) >= 0.5:
        score += 0.4
    if submission_result.get("success"):
        score += 0.3
    
    grade = "A" if score >= 0.9 else "B" if score >= 0.7 else "C" if score >= 0.5 else "D"
    
    print(f"\n🎓 Final Grade: {grade}")
    print(f"🎯 Score: {score:.1f}/1.0")
    
    if submission_result.get("success"):
        print(f"\n🚀 READY FOR MERCOR SUBMISSION!")
        print("Submit with:")
        print("curl -H 'Authorization: bhaumik.tandan@gmail.com' \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d @final_submission.json \\")
        print("     'https://mercor-dev--search-eng-interview.modal.run/grade'")

if __name__ == "__main__":
    main() 