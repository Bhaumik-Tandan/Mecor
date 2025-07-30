#!/usr/bin/env python3
"""
Mercor Search Agent - Retrieval Example
Demonstrates how to use the search system and evaluate results.

This example shows:
1. How to query the search system
2. How to call the evaluation API
3. How to interpret results

Author: Bhaumik Tandan
"""

import os
import sys
import json
import requests
from typing import List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy
from src.utils.logger import setup_logger

def search_candidates(query_text: str, job_category: str, max_candidates: int = 100) -> List[str]:
    """
    Search for candidates based on query text and job category.
    
    Args:
        query_text: The search query describing desired candidate profile
        job_category: The job category (e.g., "tax_lawyer.yml")
        max_candidates: Maximum number of candidates to return (up to 100)
    
    Returns:
        List of candidate IDs
    """
    logger = setup_logger("retrieval_example")
    
    try:
        # Initialize search service
        search_service = SearchService()
        
        # Create search query
        query = SearchQuery(
            query_text=query_text,
            job_category=job_category,
            strategy=SearchStrategy.HYBRID,  # Use hybrid for best results
            max_candidates=max_candidates
        )
        
        # Execute search
        logger.info(f"🔍 Searching for: {query_text}")
        logger.info(f"📂 Category: {job_category}")
        
        candidates = search_service.search_candidates(query)
        candidate_ids = [c.id for c in candidates]
        
        logger.info(f"🎯 Found {len(candidate_ids)} candidates")
        return candidate_ids
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        return []

def evaluate_candidates(category: str, candidate_ids: List[str]) -> dict:
    """
    Evaluate candidates using the Mercor evaluation API.
    
    Args:
        category: The job category (e.g., "tax_lawyer.yml")
        candidate_ids: List of candidate IDs to evaluate
    
    Returns:
        Dictionary containing evaluation results
    """
    logger = setup_logger("retrieval_example")
    
    try:
        logger.info(f"📊 Evaluating {len(candidate_ids)} candidates for {category}")
        
        # Call Mercor evaluation API
        response = requests.post(
            "https://mercor-dev--search-eng-interview.modal.run/evaluate",
            headers={
                "Authorization": "bhaumik.tandan@gmail.com",
                "Content-Type": "application/json"
            },
            json={
                "config_path": category,
                "object_ids": candidate_ids[:10]  # Limit to 10 for evaluation
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            overall_score = data.get('average_final_score', 0)
            
            logger.info(f"✅ Evaluation successful!")
            logger.info(f"📈 Overall Score: {overall_score:.3f}")
            
            return {
                "success": True,
                "overall_score": overall_score,
                "detailed_results": data
            }
        else:
            logger.error(f"❌ API returned status {response.status_code}")
            return {"success": False, "error": f"API error: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"❌ Evaluation failed: {e}")
        return {"success": False, "error": str(e)}

def example_tax_lawyer_search():
    """Example: Search and evaluate tax lawyers."""
    print("🏛️ Example: Tax Lawyer Search")
    print("="*50)
    
    # Define search parameters
    query_text = "tax attorney JD Harvard Yale Stanford Columbia BigLaw Skadden Kirkland partner"
    category = "tax_lawyer.yml"
    
    # Search for candidates
    candidate_ids = search_candidates(query_text, category, max_candidates=50)
    
    if not candidate_ids:
        print("❌ No candidates found")
        return
    
    print(f"Found candidates: {candidate_ids[:5]}...")  # Show first 5 IDs
    
    # Evaluate candidates
    results = evaluate_candidates(category, candidate_ids)
    
    if results["success"]:
        print(f"🎯 Overall Score: {results['overall_score']:.3f}")
        
        # Print detailed breakdown if available
        detailed = results.get("detailed_results", {})
        if "average_soft_scores" in detailed:
            print("\n📊 Soft Criteria Breakdown:")
            for criteria in detailed["average_soft_scores"]:
                name = criteria.get("criteria_name", "Unknown")
                score = criteria.get("average_score", 0)
                print(f"  • {name}: {score:.2f}")
        
        if "average_hard_scores" in detailed:
            print("\n✅ Hard Criteria Pass Rates:")
            for criteria in detailed["average_hard_scores"]:
                name = criteria.get("criteria_name", "Unknown")
                rate = criteria.get("pass_rate", 0)
                print(f"  • {name}: {rate:.1%}")
    else:
        print(f"❌ Evaluation failed: {results.get('error', 'Unknown error')}")

def example_biology_expert_search():
    """Example: Search and evaluate biology experts."""
    print("\n🧬 Example: Biology Expert Search")
    print("="*50)
    
    # Define search parameters  
    query_text = "PhD Biology Harvard MIT Stanford professor publications Nature Science CRISPR"
    category = "biology_expert.yml"
    
    # Search for candidates
    candidate_ids = search_candidates(query_text, category, max_candidates=50)
    
    if not candidate_ids:
        print("❌ No candidates found")
        return
    
    print(f"Found candidates: {candidate_ids[:5]}...")  # Show first 5 IDs
    
    # Evaluate candidates
    results = evaluate_candidates(category, candidate_ids)
    
    if results["success"]:
        print(f"🎯 Overall Score: {results['overall_score']:.3f}")
    else:
        print(f"❌ Evaluation failed: {results.get('error', 'Unknown error')}")

def main():
    """Main function demonstrating retrieval and evaluation."""
    print("🚀 Mercor Search Agent - Retrieval Example")
    print("="*60)
    print()
    
    # Load environment
    from src.utils.env_loader import load_environment
    load_environment()
    
    # Run examples
    try:
        example_tax_lawyer_search()
        example_biology_expert_search()
        
        print("\n" + "="*60)
        print("✅ Retrieval examples completed!")
        print("💡 Tips:")
        print("  • Use specific search terms for better results")
        print("  • Hybrid search strategy works best for most categories")
        print("  • Evaluation API accepts up to 10 candidates at a time")
        print("  • Check logs/ directory for detailed execution logs")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("💡 Make sure to run 'python init.py' first to set up the system")

if __name__ == "__main__":
    main() 