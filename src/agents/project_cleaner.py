#!/usr/bin/env python3
"""
Project Structure Cleaner Agent
===============================

Intelligent agent that cleans up project structure, removes useless files,
and organizes the codebase for professional submission.
"""

import os
import shutil
import glob
from typing import List, Dict, Set
from pathlib import Path

class ProjectCleanerAgent:
    """
    Agent responsible for maintaining clean, professional project structure.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.files_to_keep = self._define_essential_files()
        self.directories_to_keep = self._define_essential_directories()
        
    def _define_essential_files(self) -> Set[str]:
        """Define files that should be kept."""
        return {
            # Core application files
            "src/main.py",
            "src/config/settings.py", 
            "src/config/prompts.json",
            "src/models/candidate.py",
            "src/services/search_service.py",
            "src/services/gpt_service.py", 
            "src/services/embedding_service.py",
            "src/services/evaluation_service.py",
            "src/agents/validation_agent.py",
            "src/agents/project_cleaner.py",
            "src/utils/logger.py",
            "src/utils/helpers.py",
            
            # Infrastructure files
            "requirements.txt",
            "setup.py",
            ".env",
            "environment_template.txt",
            ".gitignore",
            
            # Submission files
            "create_final_submission.py",
            "migrate_to_turbo.py",
            "quick_start.sh",
            
            # Documentation
            "README.md"
        }
    
    def _define_essential_directories(self) -> Set[str]:
        """Define directories that should be kept."""
        return {
            "src",
            "src/config", 
            "src/models",
            "src/services", 
            "src/agents",
            "src/utils",
            "venv"
        }
    
    def analyze_project_structure(self) -> Dict[str, List[str]]:
        """Analyze current project structure and categorize files."""
        
        analysis = {
            "essential_files": [],
            "useless_files": [],
            "duplicate_files": [],
            "large_files": [],
            "empty_directories": []
        }
        
        # Scan all files
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(self.project_root))
                
                # Skip hidden files and venv
                if any(part.startswith('.') for part in file_path.parts) or 'venv' in file_path.parts:
                    if relative_path not in self.files_to_keep:
                        continue
                
                # Categorize files
                if relative_path in self.files_to_keep:
                    analysis["essential_files"].append(relative_path)
                elif self._is_useless_file(file_path):
                    analysis["useless_files"].append(relative_path)
                elif file_path.stat().st_size > 10 * 1024 * 1024:  # > 10MB
                    analysis["large_files"].append(f"{relative_path} ({file_path.stat().st_size // (1024*1024)}MB)")
        
        # Find empty directories
        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                relative_path = str(dir_path.relative_to(self.project_root))
                analysis["empty_directories"].append(relative_path)
        
        # Find potential duplicates
        analysis["duplicate_files"] = self._find_duplicate_files()
        
        return analysis
    
    def _is_useless_file(self, file_path: Path) -> bool:
        """Determine if a file is useless and can be removed."""
        
        useless_patterns = [
            # Old script versions
            "*search_agent*.py",
            "*test_script*.py", 
            "*_improved.py",
            "*_final.py",
            "*_optimized.py",
            "*_enhanced.py",
            
            # Log files
            "*.log",
            "*logs*",
            
            # Temporary files
            "*.tmp",
            "*.temp",
            "*~",
            "*.bak",
            
            # Generated files
            "*submission_format_example.json",
            "*test_soft_filters.py",
            "*test_domain_validation.py",
            
            # Documentation files (keeping only README.md)
            "README_IMPROVEMENTS.md",
            "PROJECT_STRUCTURE.md",
            
            # Build/cache files
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".pytest_cache",
            
            # IDE files
            ".vscode",
            ".idea",
            "*.swp"
        ]
        
        file_name = file_path.name
        relative_path = str(file_path.relative_to(self.project_root))
        
        for pattern in useless_patterns:
            if file_path.match(pattern) or relative_path in pattern:
                return True
        
        # Check if it's an intermediate submission file
        if "submission" in file_name.lower() and file_name != "create_final_submission.py":
            return True
            
        return False
    
    def _find_duplicate_files(self) -> List[str]:
        """Find potential duplicate files."""
        
        duplicates = []
        
        # Look for common duplicate patterns
        duplicate_patterns = [
            ("search_agent.py", "*search_agent*.py"),
            ("main.py", "*main*.py"),
            ("README.md", "README*.md")
        ]
        
        for base_file, pattern in duplicate_patterns:
            matches = list(self.project_root.glob(pattern))
            if len(matches) > 1:
                duplicates.extend([str(p.relative_to(self.project_root)) for p in matches if p.name != base_file])
        
        return duplicates
    
    def clean_project(self, dry_run: bool = True) -> Dict[str, int]:
        """Clean the project structure."""
        
        analysis = self.analyze_project_structure()
        
        stats = {
            "files_removed": 0,
            "directories_removed": 0,
            "space_saved_mb": 0
        }
        
        print(f"🧹 Project Cleanup {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
        print("=" * 60)
        
        # Remove useless files
        if analysis["useless_files"]:
            print(f"📁 Removing {len(analysis['useless_files'])} useless files:")
            for file_path in analysis["useless_files"]:
                full_path = self.project_root / file_path
                if full_path.exists():
                    size_mb = full_path.stat().st_size / (1024 * 1024)
                    print(f"  ❌ {file_path} ({size_mb:.1f}MB)")
                    
                    if not dry_run:
                        full_path.unlink()
                        stats["files_removed"] += 1
                        stats["space_saved_mb"] += size_mb
        
        # Remove duplicate files
        if analysis["duplicate_files"]:
            print(f"\n🔄 Removing {len(analysis['duplicate_files'])} duplicate files:")
            for file_path in analysis["duplicate_files"]:
                full_path = self.project_root / file_path
                if full_path.exists():
                    print(f"  ❌ {file_path}")
                    if not dry_run:
                        full_path.unlink()
                        stats["files_removed"] += 1
        
        # Remove empty directories
        if analysis["empty_directories"]:
            print(f"\n📂 Removing {len(analysis['empty_directories'])} empty directories:")
            for dir_path in analysis["empty_directories"]:
                full_path = self.project_root / dir_path
                if full_path.exists() and full_path.is_dir():
                    print(f"  ❌ {dir_path}/")
                    if not dry_run:
                        full_path.rmdir()
                        stats["directories_removed"] += 1
        
        # Show what's being kept
        print(f"\n✅ Keeping {len(analysis['essential_files'])} essential files:")
        for file_path in sorted(analysis["essential_files"])[:10]:  # Show first 10
            print(f"  ✓ {file_path}")
        
        if len(analysis["essential_files"]) > 10:
            print(f"  ... and {len(analysis['essential_files']) - 10} more")
        
        print(f"\n📊 Cleanup Summary:")
        print(f"  Files removed: {stats['files_removed']}")
        print(f"  Directories removed: {stats['directories_removed']}")
        print(f"  Space saved: {stats['space_saved_mb']:.1f}MB")
        
        return stats
    
    def organize_structure(self, dry_run: bool = True) -> bool:
        """Organize project structure according to best practices."""
        
        print(f"\n🏗️ Organizing Project Structure {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
        print("=" * 60)
        
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
                if not dry_run:
                    full_path.mkdir(parents=True, exist_ok=True)
        
        # Move misplaced files to correct locations
        file_moves = [
            ("validation_agent.py", "src/agents/validation_agent.py"),
            ("project_cleaner.py", "src/agents/project_cleaner.py")
        ]
        
        for source, target in file_moves:
            source_path = self.project_root / source
            target_path = self.project_root / target
            
            if source_path.exists() and not target_path.exists():
                print(f"📦 Moving: {source} → {target}")
                if not dry_run:
                    shutil.move(str(source_path), str(target_path))
        
        print("✅ Project structure organized")
        return True 