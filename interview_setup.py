#!/usr/bin/env python3
"""
Interview Setup and Validation Script
====================================

This script validates that your system is ready for the interview testing.
Run this before the interview to ensure everything is working properly.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_environment():
    """Check if all required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    try:
        from src.utils.env_loader import env_loader
        
        required_vars = [
            'USER_EMAIL',
            'TURBOPUFFER_API_KEY',
            'VOYAGE_API_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = env_loader.get(var, '')
            if not value:
                missing_vars.append(var)
            else:
                print(f"  ✅ {var}: {'*' * min(len(value), 8)}...")
        
        if missing_vars:
            print(f"  ❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        print("  ✅ All required environment variables are set")
        return True
        
    except Exception as e:
        print(f"  ❌ Error checking environment: {e}")
        return False

def check_dependencies():
    """Check if all required Python packages are installed."""
    print("\n📦 Checking Python dependencies...")
    
    required_packages = [
        'turbopuffer',
        'requests',
        'psutil',
        'pathlib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} (missing)")
    
    if missing_packages:
        print(f"  ❌ Missing packages: {', '.join(missing_packages)}")
        print("  💡 Run: pip install -r requirements.txt")
        return False
    
    print("  ✅ All required packages are installed")
    return True

def check_file_structure():
    """Check if all required files and directories exist."""
    print("\n📁 Checking file structure...")
    
    required_files = [
        'src/main.py',
        'src/config/settings.py',
        'src/services/search_service.py',
        'src/services/evaluation_service.py',
        'interview_testing_script.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"  ❌ {file_path} (missing)")
    
    if missing_files:
        print(f"  ❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("  ✅ All required files exist")
    return True

def test_imports():
    """Test if all modules can be imported successfully."""
    print("\n🔧 Testing imports...")
    
    try:
        from src.config.settings import config
        print("  ✅ src.config.settings")
    except Exception as e:
        print(f"  ❌ src.config.settings: {e}")
        return False
    
    try:
        from src.models.candidate import SearchQuery, SearchStrategy
        print("  ✅ src.models.candidate")
    except Exception as e:
        print(f"  ❌ src.models.candidate: {e}")
        return False
    
    try:
        from src.services.search_service import search_service
        print("  ✅ src.services.search_service")
    except Exception as e:
        print(f"  ❌ src.services.search_service: {e}")
        return False
    
    try:
        from src.services.evaluation_service import evaluation_service
        print("  ✅ src.services.evaluation_service")
    except Exception as e:
        print(f"  ❌ src.services.evaluation_service: {e}")
        return False
    
    print("  ✅ All imports successful")
    return True

def test_basic_functionality():
    """Test basic functionality without making API calls."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from src.config.settings import config
        from src.models.candidate import SearchQuery, SearchStrategy
        
        # Test creating a search query
        query = SearchQuery(
            query_text="test query",
            job_category="test",
            strategy=SearchStrategy.HYBRID,
            max_candidates=5
        )
        print("  ✅ SearchQuery creation")
        
        # Test configuration loading
        if config.api.user_email:
            print("  ✅ Configuration loaded")
        else:
            print("  ❌ Configuration not loaded properly")
            return False
        
        print("  ✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        return False

def main():
    """Main validation function."""
    print("🚀 Mercor Interview Setup Validation")
    print("=" * 50)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"  ❌ {check_name} check failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Your system is ready for the interview.")
        print("\n📋 Quick start commands:")
        print("  python interview_testing_script.py --interactive")
        print("  python interview_testing_script.py --query 'your query here'")
        print("  python interview_testing_script.py --batch-file example_queries.txt")
    else:
        print("❌ Some checks failed. Please fix the issues above before the interview.")
        print("\n💡 Common fixes:")
        print("  1. Set up your .env file with required API keys")
        print("  2. Install missing packages: pip install -r requirements.txt")
        print("  3. Ensure all source files are in the correct locations")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 