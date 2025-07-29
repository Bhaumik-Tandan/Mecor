#!/usr/bin/env python3

import os
import sys
import json
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy

def retrieve_candidates(query_text: str, category: str, max_candidates: int = 100):
    """
    Retrieval Logic: Takes a query and returns up to 100 candidate IDs.
    
    Args:
        query_text: Search query string
        category: Job category (e.g., "biology_expert.yml")
        max_candidates: Maximum number of candidates to return (up to 100)
    
    Returns:
        List of candidate IDs
    """
    search_service = SearchService()
    
    query = SearchQuery(
        query_text=query_text,
        job_category=category,
        strategy=SearchStrategy.VECTOR_ONLY,
        max_candidates=max_candidates
    )
    
    candidates = search_service.search_candidates(query)
    candidate_ids = [c.id for c in candidates]
    
    print(f"Query: '{query_text}'")
    print(f"Category: {category}")
    print(f"Found: {len(candidate_ids)} candidates")
    
    return candidate_ids

def evaluate_candidates(category: str, candidate_ids: list):
    """
    Example of calling the evaluation API and printing the overallScore.
    
    Args:
        category: Job category configuration file
        candidate_ids: List of candidate IDs to evaluate
    
    Returns:
        Overall score from evaluation API
    """
    try:
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
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            overall_score = data.get('overallScore', 0)
            
            print(f"\n📊 EVALUATION RESULTS:")
            print(f"Category: {category}")
            print(f"Candidates evaluated: {len(candidate_ids[:10])}")
            print(f"Overall Score: {overall_score}")
            
            return overall_score
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return 0
            
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return 0

def main():
    """Demonstration of retrieval and evaluation workflow."""
    print("🔍 RETRIEVAL LOGIC EXAMPLE")
    print("=" * 40)
    
    # Example query
    query_text = "PhD biology research molecular genetics university professor"
    category = "biology_expert.yml"
    
    # Step 1: Retrieve candidates
    candidate_ids = retrieve_candidates(query_text, category, max_candidates=20)
    
    if candidate_ids:
        print(f"\n✅ Retrieved {len(candidate_ids)} candidates")
        print(f"Sample IDs: {candidate_ids[:5]}")
        
        # Step 2: Evaluate candidates
        score = evaluate_candidates(category, candidate_ids)
        
        if score > 0:
            print(f"\n🎯 Success! Score: {score}")
        else:
            print(f"\n⚠️ Evaluation returned score: {score}")
    else:
        print("\n❌ No candidates found")

if __name__ == "__main__":
    main() 