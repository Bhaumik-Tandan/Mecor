#!/usr/bin/env python3
"""
AI Orchestrator - Master Intelligent Agent
==========================================

Central AI agent that orchestrates the entire search and submission process.
Validates outputs, triggers improvements, monitors scope, and maintains project quality.
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.validation_agent import validation_agent, ValidationStatus
from src.agents.project_cleaner import ProjectCleanerAgent
from src.models.candidate import SearchQuery, SearchStrategy
from src.services.evaluation_service import evaluation_service
from src.utils.logger import setup_logger

logger = setup_logger("ai_orchestrator", level="INFO")

class AIOrchestrator:
    """
    Master AI agent that orchestrates the entire intelligent search system.
    """
    
    def __init__(self):
        self.cleaner = ProjectCleanerAgent()
        self.performance_history = []
        self.current_session = None
        
        logger.info("🤖 AI Orchestrator initialized")
    
    def run_full_optimization_cycle(self, cleanup_project: bool = True) -> Dict[str, Any]:
        """
        Run complete optimization cycle: cleanup, validate, improve, and generate submission.
        """
        print("🚀 AI ORCHESTRATOR - FULL OPTIMIZATION CYCLE")
        print("=" * 80)
        print("Intelligent AI agent coordinating search optimization and submission")
        print()
        
        results = {
            "cleanup": {},
            "validation_tests": {},
            "submission_generation": {},
            "final_assessment": {},
            "duration": 0
        }
        
        start_time = time.time()
        
        # Step 1: Project cleanup and organization
        if cleanup_project:
            print("📋 STEP 1: Project Structure Optimization")
            print("-" * 50)
            results["cleanup"] = self._execute_project_cleanup()
        
        # Step 2: Validation and quality testing
        print("\n📋 STEP 2: Intelligent Search Validation")
        print("-" * 50)
        results["validation_tests"] = self._execute_validation_tests()
        
        # Step 3: Generate optimized submission
        print("\n📋 STEP 3: Generate Final Submission")
        print("-" * 50)
        results["submission_generation"] = self._generate_final_submission()
        
        # Step 4: Final assessment and recommendations
        print("\n📋 STEP 4: Final Assessment")
        print("-" * 50)
        results["final_assessment"] = self._generate_final_assessment(results)
        
        results["duration"] = time.time() - start_time
        
        # Generate comprehensive report
        self._generate_orchestrator_report(results)
        
        return results
    
    def _execute_project_cleanup(self) -> Dict[str, Any]:
        """Execute intelligent project cleanup."""
        
        # First analyze what needs cleaning
        analysis = self.cleaner.analyze_project_structure()
        
        print(f"📊 Project Analysis:")
        print(f"  Essential files: {len(analysis['essential_files'])}")
        print(f"  Useless files: {len(analysis['useless_files'])}")
        print(f"  Duplicate files: {len(analysis['duplicate_files'])}")
        print(f"  Empty directories: {len(analysis['empty_directories'])}")
        
        # Show what will be cleaned
        if analysis['useless_files']:
            print(f"\n🗑️  Files to remove:")
            for file in analysis['useless_files'][:5]:  # Show first 5
                print(f"    ❌ {file}")
            if len(analysis['useless_files']) > 5:
                print(f"    ... and {len(analysis['useless_files']) - 5} more")
        
        # Ask for confirmation (simulate intelligent decision)
        should_clean = len(analysis['useless_files']) > 0 or len(analysis['duplicate_files']) > 0
        
        if should_clean:
            print(f"\n🤖 AI Decision: Cleanup recommended - {len(analysis['useless_files']) + len(analysis['duplicate_files'])} files to remove")
            
            # Execute cleanup
            cleanup_stats = self.cleaner.clean_project(dry_run=False)
            self.cleaner.organize_structure(dry_run=False)
            
            return {
                "executed": True,
                "stats": cleanup_stats,
                "analysis": analysis
            }
        else:
            print("✅ Project structure already optimal")
            return {
                "executed": False,
                "reason": "No cleanup needed"
            }
    
    def _execute_validation_tests(self) -> Dict[str, Any]:
        """Execute comprehensive validation tests across different domains."""
        
        test_categories = [
            "mathematics_phd.yml",
            "biology_expert.yml", 
            "radiology.yml",
            "tax_lawyer.yml"
        ]
        
        validation_results = {}
        overall_scores = []
        
        print("🧪 Testing search quality across domains...")
        
        for category in test_categories:
            print(f"\n🔍 Testing: {category}")
            
            # Create test query
            query = SearchQuery(
                query_text=f"expert professional {category.replace('_', ' ').replace('.yml', '')}",
                job_category=category,
                strategy=SearchStrategy.HYBRID,
                max_candidates=10
            )
            
            # Run orchestrated search with validation
            session_id = f"test_{category}_{int(time.time())}"
            candidates, validations = validation_agent.orchestrate_search(query, session_id)
            
            # Get final validation result
            final_validation = validations[-1] if validations else None
            
            if final_validation:
                status_emoji = {
                    ValidationStatus.EXCELLENT: "🟢",
                    ValidationStatus.GOOD: "🟡", 
                    ValidationStatus.MODERATE: "🟠",
                    ValidationStatus.POOR: "🔴",
                    ValidationStatus.FAILED: "❌"
                }.get(final_validation.status, "❓")
                
                print(f"  {status_emoji} Score: {final_validation.score:.2f} ({final_validation.status.value})")
                print(f"  📝 {final_validation.reasoning}")
                
                overall_scores.append(final_validation.score)
                
                validation_results[category] = {
                    "score": final_validation.score,
                    "status": final_validation.status.value,
                    "candidates_found": len(candidates),
                    "iterations": len(validations),
                    "reasoning": final_validation.reasoning
                }
            else:
                print("  ❌ Validation failed")
                validation_results[category] = {
                    "score": 0.0,
                    "status": "failed",
                    "candidates_found": len(candidates),
                    "error": "No validation performed"
                }
        
        # Calculate overall performance
        avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        
        print(f"\n📊 Overall Validation Summary:")
        print(f"  Average Score: {avg_score:.2f}")
        print(f"  Categories Tested: {len(test_categories)}")
        print(f"  Success Rate: {len([s for s in overall_scores if s >= 0.7]) / len(overall_scores) * 100:.1f}%")
        
        return {
            "average_score": avg_score,
            "category_results": validation_results,
            "success_rate": len([s for s in overall_scores if s >= 0.7]) / len(overall_scores) if overall_scores else 0
        }
    
    def _generate_final_submission(self) -> Dict[str, Any]:
        """Generate the final optimized submission."""
        
        try:
            # Import and run the submission generator
            sys.path.insert(0, '.')
            
            print("🎯 Generating final submission with AI-validated candidates...")
            
            # Execute the submission generator
            import subprocess
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
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            logger.error(f"Submission generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_final_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final assessment and recommendations."""
        
        assessment = {
            "overall_grade": "unknown",
            "strengths": [],
            "areas_for_improvement": [],
            "ready_for_submission": False,
            "confidence_score": 0.0
        }
        
        # Calculate overall confidence score
        factors = []
        
        # Project cleanup factor
        if results["cleanup"].get("executed"):
            factors.append(0.9)  # Clean project
            assessment["strengths"].append("Clean, professional project structure")
        else:
            factors.append(0.8)  # Already clean
        
        # Validation factor
        validation_score = results["validation_tests"].get("average_score", 0)
        factors.append(validation_score)
        
        if validation_score >= 0.8:
            assessment["strengths"].append("Excellent search quality validation")
        elif validation_score >= 0.6:
            assessment["strengths"].append("Good search quality validation")
        else:
            assessment["areas_for_improvement"].append("Search quality needs improvement")
        
        # Submission factor
        if results["submission_generation"].get("success"):
            factors.append(0.9)
            assessment["strengths"].append("Successful submission generation")
        else:
            factors.append(0.3)
            assessment["areas_for_improvement"].append("Submission generation failed")
        
        # Calculate confidence
        assessment["confidence_score"] = sum(factors) / len(factors) if factors else 0.0
        
        # Determine grade
        if assessment["confidence_score"] >= 0.9:
            assessment["overall_grade"] = "A+"
            assessment["ready_for_submission"] = True
        elif assessment["confidence_score"] >= 0.8:
            assessment["overall_grade"] = "A"
            assessment["ready_for_submission"] = True
        elif assessment["confidence_score"] >= 0.7:
            assessment["overall_grade"] = "B+"
            assessment["ready_for_submission"] = True
        elif assessment["confidence_score"] >= 0.6:
            assessment["overall_grade"] = "B"
        else:
            assessment["overall_grade"] = "C"
            assessment["areas_for_improvement"].append("Significant improvements needed")
        
        # Display assessment
        print(f"🎓 Final Grade: {assessment['overall_grade']}")
        print(f"🎯 Confidence Score: {assessment['confidence_score']:.2f}")
        print(f"🚀 Ready for Submission: {'YES' if assessment['ready_for_submission'] else 'NO'}")
        
        if assessment["strengths"]:
            print(f"\n✅ Strengths:")
            for strength in assessment["strengths"]:
                print(f"  • {strength}")
        
        if assessment["areas_for_improvement"]:
            print(f"\n🔧 Areas for Improvement:")
            for area in assessment["areas_for_improvement"]:
                print(f"  • {area}")
        
        return assessment
    
    def _generate_orchestrator_report(self, results: Dict[str, Any]) -> None:
        """Generate comprehensive orchestrator report."""
        
        report_file = "AI_ORCHESTRATOR_REPORT.md"
        
        report_content = f"""# AI Orchestrator Report
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}

## 🎯 Executive Summary
- **Duration**: {results['duration']:.1f} seconds
- **Overall Grade**: {results['final_assessment']['overall_grade']}
- **Confidence Score**: {results['final_assessment']['confidence_score']:.2f}
- **Ready for Submission**: {results['final_assessment']['ready_for_submission']}

## 📋 Process Overview

### 1. Project Cleanup
"""
        
        if results["cleanup"].get("executed"):
            stats = results["cleanup"]["stats"]
            report_content += f"""
- **Status**: Executed
- **Files Removed**: {stats['files_removed']}
- **Directories Removed**: {stats['directories_removed']}
- **Space Saved**: {stats['space_saved_mb']:.1f}MB
"""
        else:
            report_content += "- **Status**: Skipped (project already clean)\n"
        
        report_content += f"""
### 2. Search Validation
- **Average Score**: {results['validation_tests']['average_score']:.2f}
- **Success Rate**: {results['validation_tests']['success_rate'] * 100:.1f}%

### 3. Submission Generation
- **Status**: {'Success' if results['submission_generation'].get('success') else 'Failed'}
"""
        
        if results['submission_generation'].get('success'):
            report_content += f"""- **Categories**: {results['submission_generation']['categories']}
- **Total Candidates**: {results['submission_generation']['total_candidates']}
"""
        
        report_content += f"""
## 🏆 Final Assessment

### Strengths
"""
        for strength in results['final_assessment']['strengths']:
            report_content += f"- {strength}\n"
        
        if results['final_assessment']['areas_for_improvement']:
            report_content += f"\n### Areas for Improvement\n"
            for area in results['final_assessment']['areas_for_improvement']:
                report_content += f"- {area}\n"
        
        report_content += f"""
## 🚀 Next Steps
{'✅ Ready to submit to Mercor!' if results['final_assessment']['ready_for_submission'] else '⚠️ Address improvements before submission'}

---
Generated by AI Orchestrator - Intelligent Search Optimization Agent
"""
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"\n📄 Comprehensive report saved: {report_file}")

def main():
    """Main execution function."""
    
    print("🤖 AI ORCHESTRATOR - INTELLIGENT SEARCH OPTIMIZATION")
    print("=" * 80)
    print("Master AI agent coordinating validation, optimization, and submission")
    print()
    
    orchestrator = AIOrchestrator()
    results = orchestrator.run_full_optimization_cycle(cleanup_project=True)
    
    print(f"\n🎉 AI ORCHESTRATOR COMPLETE!")
    print(f"Duration: {results['duration']:.1f}s")
    print(f"Grade: {results['final_assessment']['overall_grade']}")
    
    if results['final_assessment']['ready_for_submission']:
        print("\n🚀 READY FOR MERCOR SUBMISSION!")
        print("Run: curl -H 'Authorization: bhaumik.tandan@gmail.com' \\")
        print("          -H 'Content-Type: application/json' \\") 
        print("          -d @final_submission.json \\")
        print("          'https://mercor-dev--search-eng-interview.modal.run/grade'")
    else:
        print("\n⚠️ Improvements needed before submission")

if __name__ == "__main__":
    main() 