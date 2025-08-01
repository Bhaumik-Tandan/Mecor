#!/usr/bin/env python3
"""
Submit Correct Format
=====================
Submit using the exact format the API expects: config_candidates field
"""

import sys
import json
import requests
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import SearchAgent
from src.models.candidate import SearchQuery, SearchStrategy

def submit_single_category_correct(category, candidate_ids, user_email):
    """Submit using the correct format that API expects."""
    print(f"\n📤 SUBMITTING {category}")
    print("=" * 50)
    
    if len(candidate_ids) != 10:
        print(f"⚠️ Category has {len(candidate_ids)} candidates (need exactly 10)")
        return None
    
    # Use the format the API actually expects based on error message
    payload = {
        "config_candidates": {
            category: candidate_ids
        }
    }
    
    grade_url = "https://mercor-dev--search-eng-interview.modal.run/grade"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": user_email
    }
    
    try:
        print(f"🚀 Submitting {category} with {len(candidate_ids)} candidates...")
        print(f"📋 Payload structure: config_candidates -> {category}")
        
        response = requests.post(
            grade_url,
            json=payload,
            headers=headers,
            timeout=120
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 SUCCESS!")
            
            # Extract score if available
            if 'results' in result and category in result['results']:
                score = result['results'][category].get('average_final_score', 'N/A')
                status = "✅" if score >= 30.0 else "❌"
                print(f"   {status} Score: {score}")
                return {"category": category, "score": score, "success": True}
            else:
                print(f"   Response: {result}")
                return {"category": category, "score": None, "success": True}
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return {"category": category, "score": None, "success": False, "error": response.text}
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"category": category, "score": None, "success": False, "error": str(e)}

def quick_test_biology():
    """Quick test with biology_expert.yml since we know it works."""
    print("🧬 QUICK TEST: biology_expert.yml")
    print("=" * 60)
    
    user_email = "bhaumik.tandan@gmail.com"
    search_agent = SearchAgent()
    
    # Use successful biology search terms
    biology_terms = [
        "Harvard MIT Stanford biology professor PhD researcher",
        "Nature Science Cell publication molecular biology"
    ]
    
    print("🔍 Collecting candidates...")
    all_candidates = set()
    
    for term in biology_terms:
        print(f"   Searching: {term[:50]}...")
        
        query = SearchQuery(
            query_text=term,
            job_category="biology_expert.yml",
            strategy=SearchStrategy.HYBRID,
            max_candidates=300
        )
        
        try:
            candidates = search_agent.search_service.search_candidates(
                query, SearchStrategy.HYBRID
            )
            
            for candidate in candidates:
                all_candidates.add(candidate.id)
            
            print(f"   Found: {len(candidates)} | Total: {len(all_candidates)}")
            
            if len(all_candidates) >= 10:
                break
                
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
            continue
    
    candidate_ids = list(all_candidates)[:10]
    print(f"✅ Selected {len(candidate_ids)} candidates")
    
    if len(candidate_ids) == 10:
        # Test submission
        result = submit_single_category_correct("biology_expert.yml", candidate_ids, user_email)
        return result
    else:
        print(f"❌ Only got {len(candidate_ids)} candidates")
        return None

def main():
    """Main execution - quick test first."""
    print("🎓 CORRECT FORMAT SUBMISSION TEST")
    print("=" * 70)
    
    try:
        # Quick test with biology first
        result = quick_test_biology()
        
        if result:
            print(f"\n📊 TEST RESULT:")
            if result['success']:
                status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
                score_text = f" - Score: {result['score']}" if result['score'] is not None else ""
                print(f"{status} {result['category']}{score_text}")
                
                if result['score'] is not None and result['score'] >= 30.0:
                    print("🎉 Score above 30!")
            else:
                print(f"❌ FAILED - {result.get('error', 'Unknown error')}")
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"results/correct_format_test_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "test_category": "biology_expert.yml",
                "result": result
            }, f, indent=2)
        
        print(f"💾 Results saved: {results_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 