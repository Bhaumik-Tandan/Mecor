#!/usr/bin/env python3
"""
Test Enhanced AI Agent with Evaluation Endpoint
==============================================

Quick test to demonstrate the evaluation endpoint integration.
"""

import os
import sys
import json
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy
from src.services.search_service import search_service

def test_evaluation_endpoint():
    """Test the evaluation endpoint with a single category."""
    
    print("🔍 TESTING EVALUATION ENDPOINT INTEGRATION")
    print("=" * 60)
    
    # Test with tax lawyers
    category = "tax_lawyer.yml"
    print(f"📋 Testing category: {category}")
    
    # Step 1: Search for candidates
    query = SearchQuery(
        query_text="experienced tax attorney legal counsel IRS",
        job_category=category,
        strategy=SearchStrategy.HYBRID,
        max_candidates=20
    )
    
    candidates = search_service.search_candidates(query, SearchStrategy.HYBRID)
    print(f"✅ Found {len(candidates)} candidates using hybrid search")
    
    # Step 2: Test evaluation endpoint
    candidate_ids = [c.id for c in candidates[:10]]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": config.api.user_email
    }
    
    payload = {
        "config_path": category,
        "object_ids": candidate_ids
    }
    
    print(f"\n🔍 Calling evaluation endpoint...")
    print(f"📧 User email: {config.api.user_email}")
    print(f"👥 Candidate IDs: {len(candidate_ids)}")
    
    try:
        response = requests.post(
            "https://mercor-dev--search-eng-interview.modal.run/evaluate",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Evaluation successful!")
            print(f"📈 Overall Score: {result.get('overallScore', 'N/A')}")
            print(f"📋 Full response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Evaluation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error calling evaluation endpoint: {e}")
    
    print(f"\n🎯 This demonstrates how the enhanced agent integrates")
    print(f"   the evaluation endpoint for real-time feedback!")

if __name__ == "__main__":
    test_evaluation_endpoint() 