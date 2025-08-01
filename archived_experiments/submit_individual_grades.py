#!/usr/bin/env python3
"""
Submit Individual Grades
========================
Submit each category individually to /grade API using the correct format
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

def collect_candidates_for_category(search_agent, category, search_terms, max_candidates=10):
    """Collect candidates for a specific category."""
    print(f"🔍 Collecting candidates for {category}")
    
    all_candidates = set()
    
    for i, term in enumerate(search_terms, 1):
        print(f"   Search {i}: {term[:50]}...")
        
        query = SearchQuery(
            query_text=term,
            job_category=category,
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
            
            if len(all_candidates) >= max_candidates:
                break
                
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
            continue
    
    candidate_ids = list(all_candidates)[:max_candidates]
    print(f"✅ Selected {len(candidate_ids)} candidates for {category}")
    
    return candidate_ids

def submit_single_category(category, candidate_ids, user_email):
    """Submit a single category to /grade API."""
    print(f"\n📤 SUBMITTING {category}")
    print("=" * 50)
    
    if len(candidate_ids) != 10:
        print(f"⚠️ Category has {len(candidate_ids)} candidates (need exactly 10)")
        return None
    
    # Format according to API docs
    payload = {
        "config_path": category,
        "object_ids": candidate_ids
    }
    
    grade_url = "https://mercor-dev--search-eng-interview.modal.run/grade"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": user_email
    }
    
    try:
        print(f"🚀 Submitting {category} with {len(candidate_ids)} candidates...")
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

def main():
    """Main execution."""
    print("🎓 INDIVIDUAL GRADE SUBMISSIONS")
    print("=" * 70)
    
    user_email = "bhaumik.tandan@gmail.com"
    print(f"👤 User: {user_email}")
    
    # Define search strategies for each category
    category_strategies = {
        "biology_expert.yml": [
            "Harvard MIT Stanford biology professor PhD researcher",
            "Nature Science Cell publication molecular biology",
            "NIH NSF grant principal investigator biology"
        ],
        "quantitative_finance.yml": [
            "Goldman Sachs JPMorgan quantitative analyst",
            "hedge fund portfolio manager derivatives",
            "financial engineering MIT Stanford Wharton"
        ],
        "doctors_md.yml": [
            "Harvard Medical School Johns Hopkins physician",
            "board certified internal medicine attending MD",
            "family medicine primary care doctor"
        ],
        "anthropology.yml": [
            "anthropology professor PhD cultural researcher",
            "ethnography fieldwork anthropological research",
            "social anthropology cultural studies"
        ],
        "tax_lawyer.yml": [
            "tax attorney law firm corporate taxation",
            "tax law lawyer IRS federal taxation",
            "corporate tax attorney legal practice"
        ]
    }
    
    search_agent = SearchAgent()
    results = []
    
    print(f"\n📋 Processing {len(category_strategies)} categories...")
    
    for i, (category, search_terms) in enumerate(category_strategies.items(), 1):
        print(f"\n🎯 CATEGORY {i}/{len(category_strategies)}: {category}")
        
        # Collect candidates
        candidate_ids = collect_candidates_for_category(search_agent, category, search_terms)
        
        if len(candidate_ids) == 10:
            # Submit to grade API
            result = submit_single_category(category, candidate_ids, user_email)
            if result:
                results.append(result)
        else:
            print(f"⚠️ Skipping {category} - only {len(candidate_ids)} candidates")
        
        # Brief delay between submissions
        if i < len(category_strategies):
            print("⏱️ Brief pause...")
            time.sleep(3)
    
    # Final summary
    print("\n" + "=" * 70)
    print("🏁 SUBMISSION RESULTS")
    print("=" * 70)
    
    successful = 0
    above_30 = 0
    
    for result in results:
        if result['success']:
            successful += 1
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            score_text = f" - Score: {result['score']}" if result['score'] is not None else ""
            print(f"{status} {result['category']}{score_text}")
            
            if result['score'] is not None and result['score'] >= 30.0:
                above_30 += 1
        else:
            print(f"❌ FAILED {result['category']} - {result.get('error', 'Unknown error')}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Successful submissions: {successful}/{len(category_strategies)}")
    if above_30 > 0:
        print(f"   Categories above 30: {above_30}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"results/individual_grade_submissions_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "total_categories": len(category_strategies),
            "successful_submissions": successful,
            "results": results
        }, f, indent=2)
    
    print(f"💾 Results saved: {results_file}")

if __name__ == "__main__":
    main() 