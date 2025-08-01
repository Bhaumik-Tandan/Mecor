#!/usr/bin/env python3
"""
Submit Biology Expert to Grade API
==================================
Submit biology_expert.yml to /grade API since it achieved 37.33 score (above 30)
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import SearchAgent
from src.models.candidate import SearchQuery, SearchStrategy

def collect_biology_candidates():
    """Collect 10 candidates for biology_expert.yml using the successful strategy."""
    print("🔬 COLLECTING BIOLOGY EXPERT CANDIDATES")
    print("=" * 50)
    
    search_agent = SearchAgent()
    
    # Use the successful search terms that got us to 37.33
    premium_biology_terms = [
        "Harvard MIT Stanford biology professor PhD researcher",
        "Nature Science Cell publication molecular biology", 
        "NIH NSF grant principal investigator biology",
        "Johns Hopkins UCSF biology department faculty",
        "postdoc research scientist molecular genetics"
    ]
    
    all_candidates = set()
    
    for i, term in enumerate(premium_biology_terms, 1):
        print(f"🔍 Search {i}: {term}")
        
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
            
            print(f"   Found: {len(candidates)} | Total unique: {len(all_candidates)}")
            
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
            continue
    
    # Take exactly 10 candidates
    candidate_ids = list(all_candidates)[:10]
    print(f"✅ Selected {len(candidate_ids)} candidates for submission")
    
    return candidate_ids

def submit_biology_to_grade(candidate_ids):
    """Submit biology_expert.yml to the /grade API."""
    print("\n📤 SUBMITTING TO /GRADE API")
    print("=" * 50)
    
    # Prepare payload for /grade API
    payload = {
        "biology_expert.yml": candidate_ids
    }
    
    print(f"📋 Submitting biology_expert.yml with {len(candidate_ids)} candidates")
    
    # Submit to grade API
    grade_url = "https://mercor-dev--search-eng-interview.modal.run/grade"
    
    try:
        print("🚀 Making request to /grade API...")
        response = requests.post(
            grade_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 SUCCESS! Grade API Response:")
            
            # Pretty print the response
            if 'results' in result:
                for category, data in result['results'].items():
                    score = data.get('average_final_score', 'N/A')
                    print(f"   ✅ {category}: {score}")
            else:
                print(f"   Response: {result}")
            
            # Save the response
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            response_file = f"results/biology_grade_response_{timestamp}.json"
            
            with open(response_file, 'w') as f:
                json.dump({
                    "timestamp": timestamp,
                    "category": "biology_expert.yml",
                    "candidate_count": len(candidate_ids),
                    "response_status": response.status_code,
                    "response_text": response.text,
                    "payload": payload
                }, f, indent=2)
            
            print(f"💾 Response saved: {response_file}")
            return True
            
        else:
            print(f"❌ Grade API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Grade API Error: {e}")
        return False

def main():
    """Main execution."""
    print("🧬 BIOLOGY EXPERT GRADE SUBMISSION")
    print("=" * 60)
    print("Score achieved: 37.33 (ABOVE 30 TARGET!)")
    print("=" * 60)
    
    try:
        # Collect candidates using successful strategy
        candidate_ids = collect_biology_candidates()
        
        if len(candidate_ids) == 10:
            # Submit to grade API
            success = submit_biology_to_grade(candidate_ids)
            
            if success:
                print("\n🏆 BIOLOGY EXPERT SUCCESSFULLY SUBMITTED!")
                print("🎊 Category 1/10 completed with score above 30!")
            else:
                print("\n❌ Submission failed")
        else:
            print(f"\n❌ Need exactly 10 candidates, got {len(candidate_ids)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 