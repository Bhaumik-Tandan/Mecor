#!/usr/bin/env python3
"""
Submit Final Grade - Corrected
==============================
Submit all categories to /grade API with correct Authorization header
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

def collect_all_candidates():
    """Collect 10 candidates for each category."""
    print("📋 COLLECTING CANDIDATES FOR ALL CATEGORIES")
    print("=" * 60)
    
    search_agent = SearchAgent()
    
    # Define search strategies for each category
    category_strategies = {
        "biology_expert.yml": [
            "Harvard MIT Stanford biology professor PhD researcher",
            "Nature Science Cell publication molecular biology",
            "NIH NSF grant principal investigator biology",
            "postdoc research scientist molecular genetics"
        ],
        "quantitative_finance.yml": [
            "Goldman Sachs JPMorgan quantitative analyst trader",
            "hedge fund portfolio manager derivatives pricing",
            "financial engineering MIT Stanford Wharton MBA",
            "algorithmic trading quantitative research analyst"
        ],
        "doctors_md.yml": [
            "Harvard Medical School Johns Hopkins physician",
            "board certified internal medicine attending MD",
            "family medicine primary care doctor physician",
            "medical doctor internal medicine practice"
        ],
        "anthropology.yml": [
            "anthropology professor PhD cultural researcher",
            "ethnography fieldwork anthropological research",
            "social anthropology cultural studies academic",
            "anthropologist university research professor"
        ],
        "tax_lawyer.yml": [
            "tax attorney law firm corporate taxation",
            "tax law lawyer IRS federal taxation",
            "corporate tax attorney legal practice",
            "taxation lawyer law degree tax specialist"
        ],
        "radiology.yml": [
            "radiology physician diagnostic imaging MD",
            "radiologist medical imaging hospital physician",
            "diagnostic radiology attending physician",
            "medical imaging radiology residency trained"
        ],
        "civil_engineer.yml": [
            "civil engineer infrastructure construction project",
            "structural engineer civil engineering degree",
            "construction engineering project management",
            "civil engineering infrastructure design"
        ],
        "software_engineer.yml": [
            "software engineer Python Java developer",
            "full stack developer software engineering",
            "backend engineer software development",
            "software developer programming engineering"
        ],
        "machine_learning_engineer.yml": [
            "machine learning engineer AI ML developer",
            "data scientist machine learning Python",
            "ML engineer artificial intelligence research",
            "deep learning engineer neural networks"
        ],
        "data_scientist.yml": [
            "data scientist analytics machine learning",
            "statistical analysis data science PhD",
            "data analytics scientist research",
            "data science machine learning statistician"
        ]
    }
    
    all_candidates = {}
    
    for category, search_terms in category_strategies.items():
        print(f"\n🎯 Category: {category}")
        candidate_ids = collect_candidates_for_category(search_agent, category, search_terms)
        
        # Ensure we have exactly 10 candidates
        if len(candidate_ids) >= 10:
            all_candidates[category] = candidate_ids[:10]
        else:
            print(f"⚠️ Only got {len(candidate_ids)} candidates for {category}")
            all_candidates[category] = candidate_ids
    
    return all_candidates

def submit_to_grade_api(candidates_data, user_email):
    """Submit all candidates to the /grade API."""
    print("\n📤 SUBMITTING TO /GRADE API")
    print("=" * 60)
    
    # Filter to only include categories with exactly 10 candidates
    valid_candidates = {}
    for category, candidates in candidates_data.items():
        if len(candidates) == 10:
            valid_candidates[category] = candidates
            print(f"✅ {category}: {len(candidates)} candidates")
        else:
            print(f"⚠️ {category}: {len(candidates)} candidates (skipping - need exactly 10)")
    
    if not valid_candidates:
        print("❌ No categories have exactly 10 candidates")
        return False
    
    print(f"\n🚀 Submitting {len(valid_candidates)} categories")
    
    # Submit to grade API
    grade_url = "https://mercor-dev--search-eng-interview.modal.run/grade"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": user_email  # Use email as authorization
    }
    
    try:
        print("📡 Making request to /grade API...")
        response = requests.post(
            grade_url,
            json=valid_candidates,
            headers=headers,
            timeout=180  # 3 minutes timeout
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 SUCCESS! Grade API Response:")
            
            # Pretty print the response
            if 'results' in result:
                print("\n📊 FINAL SCORES:")
                above_30_count = 0
                for category, data in result['results'].items():
                    score = data.get('average_final_score', 'N/A')
                    status = "✅" if score >= 30.0 else "❌"
                    if score >= 30.0:
                        above_30_count += 1
                    print(f"   {status} {category}: {score}")
                
                print(f"\n🎯 Categories above 30: {above_30_count}/{len(result['results'])}")
                print(f"📈 Success rate: {(above_30_count/len(result['results']))*100:.1f}%")
            else:
                print(f"   Response: {result}")
            
            # Save the response
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            response_file = f"results/final_grade_submission_{timestamp}.json"
            
            with open(response_file, 'w') as f:
                json.dump({
                    "timestamp": timestamp,
                    "submitted_categories": len(valid_candidates),
                    "total_candidates": sum(len(candidates) for candidates in valid_candidates.values()),
                    "response_status": response.status_code,
                    "response_text": response.text,
                    "payload": valid_candidates
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
    print("🎓 FINAL GRADE SUBMISSION")
    print("=" * 70)
    
    # User email from the search agent logs
    user_email = "bhaumik.tandan@gmail.com"
    print(f"👤 User: {user_email}")
    
    try:
        # Collect candidates for all categories
        candidates_data = collect_all_candidates()
        
        print(f"\n📊 COLLECTION SUMMARY:")
        for category, candidates in candidates_data.items():
            status = "✅" if len(candidates) == 10 else "⚠️"
            print(f"   {status} {category}: {len(candidates)} candidates")
        
        # Submit to grade API
        success = submit_to_grade_api(candidates_data, user_email)
        
        if success:
            print("\n🏆 FINAL SUBMISSION COMPLETED!")
            print("🎊 All available categories submitted to /grade API!")
        else:
            print("\n❌ Submission failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 