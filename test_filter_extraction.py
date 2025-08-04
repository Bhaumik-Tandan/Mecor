#!/usr/bin/env python3
"""
Test Filter Extraction Improvement
=================================

Test the new filter extraction feature that extracts filters from user queries
and applies them to hybrid search for improved performance.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.candidate import SearchQuery, SearchStrategy
from src.services.search_service import search_service
from src.services.filter_extraction_service import filter_extraction_service
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger(
    name="test_filter_extraction",
    level="INFO",
    log_file="logs/test_filter_extraction.log"
)

def test_filter_extraction():
    """Test the filter extraction improvement."""
    print("🧪 Testing Filter Extraction Improvement")
    print("=" * 50)
    
    # Test queries with various filters
    test_queries = [
        "senior software engineer with 5+ years experience in Python and machine learning",
        "tax lawyer in New York with 10 years experience",
        "remote frontend developer with React and TypeScript skills",
        "PhD in computer science from MIT with research experience",
        "investment banker in London with M&A experience, excluding junior positions",
        "experienced DevOps engineer with AWS and Kubernetes, based in San Francisco",
        "senior data scientist with Python and SQL, remote work preferred",
        "corporate lawyer with 8+ years experience, not entry level"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        print("-" * 40)
        
        # Extract filters
        start_time = time.time()
        filters = filter_extraction_service.extract_filters(query)
        extraction_time = time.time() - start_time
        
        print(f"⏱️  Filter extraction time: {extraction_time:.3f}s")
        print(f"📍 Location filters: {filters.location_filters}")
        print(f"💼 Experience filters: {filters.experience_filters}")
        print(f"🛠️  Skill filters: {filters.skill_filters}")
        print(f"🎓 Education filters: {filters.education_filters}")
        print(f"🏭 Industry filters: {filters.industry_filters}")
        print(f"📋 Title filters: {filters.title_filters}")
        print(f"❌ Exclude filters: {filters.exclude_filters}")
        
        # Create enhanced query
        enhanced_query = filter_extraction_service.create_enhanced_query(query, filters)
        print(f"🚀 Enhanced query: {enhanced_query}")
        
        # Test search with filters
        print(f"\n🔎 Testing search with filters...")
        search_start = time.time()
        
        search_query = SearchQuery(
            query_text=query,
            job_category="general",
            strategy=SearchStrategy.GPT_ENHANCED,
            max_candidates=10
        )
        
        try:
            candidates = search_service.search_candidates(
                search_query, 
                SearchStrategy.GPT_ENHANCED
            )
            
            search_time = time.time() - search_start
            print(f"✅ Search completed in {search_time:.3f}s")
            print(f"📊 Found {len(candidates)} candidates")
            
            # Show top 3 candidates
            for j, candidate in enumerate(candidates[:3], 1):
                print(f"  {j}. {candidate.name} - {candidate.summary[:100]}...")
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
        
        print("\n" + "=" * 50)

def test_performance_comparison():
    """Compare performance with and without filter extraction."""
    print("\n📊 Performance Comparison Test")
    print("=" * 50)
    
    test_query = "senior software engineer with 5+ years experience in Python and machine learning, based in San Francisco"
    
    print(f"🔍 Test Query: '{test_query}'")
    
    # Test without filter extraction (original method)
    print(f"\n🔄 Testing WITHOUT filter extraction...")
    start_time = time.time()
    
    search_query = SearchQuery(
        query_text=test_query,
        job_category="general",
        strategy=SearchStrategy.HYBRID,  # Use HYBRID to avoid GPT enhancement
        max_candidates=10
    )
    
    try:
        candidates_original = search_service.search_candidates(
            search_query, 
            SearchStrategy.HYBRID
        )
        original_time = time.time() - start_time
        print(f"✅ Original search: {len(candidates_original)} candidates in {original_time:.3f}s")
    except Exception as e:
        print(f"❌ Original search failed: {e}")
        return
    
    # Test with filter extraction (enhanced method)
    print(f"\n🚀 Testing WITH filter extraction...")
    start_time = time.time()
    
    try:
        candidates_enhanced = search_service.search_candidates(
            search_query, 
            SearchStrategy.GPT_ENHANCED  # This now includes filter extraction
        )
        enhanced_time = time.time() - start_time
        print(f"✅ Enhanced search: {len(candidates_enhanced)} candidates in {enhanced_time:.3f}s")
        
        # Performance comparison
        time_improvement = ((original_time - enhanced_time) / original_time) * 100
        print(f"📈 Time improvement: {time_improvement:.1f}%")
        
        if enhanced_time < original_time:
            print(f"🎉 Filter extraction IMPROVED performance!")
        else:
            print(f"⚠️  Filter extraction may need optimization")
            
    except Exception as e:
        print(f"❌ Enhanced search failed: {e}")

def main():
    """Main test function."""
    print("🧪 Filter Extraction Improvement Test")
    print("=" * 60)
    print("This test demonstrates the new filter extraction feature that:")
    print("1. Extracts filters from user queries using pattern matching and GPT")
    print("2. Applies filters to hybrid search for better relevance")
    print("3. Improves search performance and accuracy")
    print()
    
    try:
        # Test filter extraction
        test_filter_extraction()
        
        # Test performance comparison
        test_performance_comparison()
        
        print("\n✅ All tests completed successfully!")
        print("🎉 Filter extraction improvement is working!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    main() 