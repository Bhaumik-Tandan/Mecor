#!/usr/bin/env python3
"""
Test script to demonstrate hard/soft criteria functionality
"""

from interview_ready import InterviewSearchAgent
from src.utils.logger import setup_logger

def test_criteria_modes():
    """Test both query-only and query-with-criteria modes."""
    
    print("🚀 Testing Interview Search System with Hard/Soft Criteria")
    print("=" * 60)
    
    agent = InterviewSearchAgent()
    
    # Test 1: Query only mode
    print("\n📋 Test 1: Query Only Mode")
    print("-" * 30)
    result1 = agent.search("software engineer", "table")
    print(f"✅ Query only mode completed: {result1['num_candidates']} candidates found")
    
    # Test 2: Query with hard criteria
    print("\n📋 Test 2: Query with Hard Criteria")
    print("-" * 30)
    hard_criteria = {
        'must_have': ['java', 'python'],
        'exclude': ['junior']
    }
    result2 = agent.search("software engineer", "table", hard_criteria=hard_criteria)
    print(f"✅ Hard criteria mode completed: {result2['num_candidates']} candidates found")
    
    # Test 3: Query with soft criteria
    print("\n📋 Test 3: Query with Soft Criteria")
    print("-" * 30)
    soft_criteria = {
        'preferred': ['senior', 'experienced']
    }
    result3 = agent.search("software engineer", "table", soft_criteria=soft_criteria)
    print(f"✅ Soft criteria mode completed: {result3['num_candidates']} candidates found")
    
    # Test 4: Query with both hard and soft criteria
    print("\n📋 Test 4: Query with Both Hard and Soft Criteria")
    print("-" * 30)
    hard_criteria = {
        'must_have': ['java', 'python'],
        'exclude': ['junior']
    }
    soft_criteria = {
        'preferred': ['senior', 'experienced', 'aws']
    }
    result4 = agent.search("software engineer", "table", hard_criteria=hard_criteria, soft_criteria=soft_criteria)
    print(f"✅ Both criteria mode completed: {result4['num_candidates']} candidates found")
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_criteria_modes() 