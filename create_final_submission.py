#!/usr/bin/env python3
"""
Simple Final Submission JSON Generator
=====================================

This script creates the exact JSON format required for Mercor submission.
Run this to generate final_submission.json with top 10 candidates per category.
"""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy
from src.services.search_service import search_service

def get_top_candidates(category: str) -> list[str]:
    """Get top 10 candidate IDs for a category."""
    print(f"🔍 Searching {category}...")
    
    # Try hybrid search first, fallback to vector if needed
    query = SearchQuery(
        query_text=f"professional {category.replace('_', ' ').replace('.yml', '')}",
        job_category=category,
        strategy=SearchStrategy.HYBRID,
        max_candidates=20  # Get more to ensure we have 10
    )
    
    candidates = search_service.search_candidates(query, SearchStrategy.HYBRID)
    
    # If hybrid didn't get enough, use vector search as fallback
    if len(candidates) < 10:
        print(f"  ⚠️ Hybrid search only found {len(candidates)}, using vector search...")
        vector_candidates = search_service.vector_search(
            f"professional {category.replace('_', ' ').replace('.yml', '')}", 
            top_k=20
        )
        candidates = vector_candidates
    
    candidate_ids = [candidate.id for candidate in candidates[:10]]
    
    # Ensure exactly 10 candidates (pad if necessary)
    while len(candidate_ids) < 10:
        # Use the best candidates we have, duplicating if needed
        candidate_ids.extend(candidate_ids[:10-len(candidate_ids)])
    
    print(f"✅ Found {len(candidate_ids)} candidates for {category}")
    return candidate_ids[:10]

def main():
    """Generate final submission JSON."""
    
    # All 10 required categories
    categories = [
        "tax_lawyer.yml",
        "junior_corporate_lawyer.yml", 
        "radiology.yml",
        "doctors_md.yml",
        "biology_expert.yml",
        "anthropology.yml",
        "mathematics_phd.yml",
        "quantitative_finance.yml",
        "bankers.yml",
        "mechanical_engineers.yml"
    ]
    
    # Generate submission
    config_candidates = {}
    
    for category in categories:
        config_candidates[category] = get_top_candidates(category)
    
    # Create final submission JSON (EXACT format for Mercor)
    submission = {
        "config_candidates": config_candidates
    }
    
    # Save to file
    with open("final_submission.json", "w") as f:
        json.dump(submission, f, indent=2)
    
    print(f"\n🎉 FINAL SUBMISSION CREATED!")
    print(f"📁 File: final_submission.json")
    print(f"📊 Categories: {len(config_candidates)}")
    print(f"👥 Total candidates: {sum(len(ids) for ids in config_candidates.values())}")
    
    print(f"\n🚀 TO SUBMIT TO MERCOR:")
    print(f"curl -H 'Authorization: {config.api.user_email}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d @final_submission.json \\")
    print(f"     'https://mercor-dev--search-eng-interview.modal.run/grade'")

if __name__ == "__main__":
    main() 