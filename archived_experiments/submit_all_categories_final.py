#!/usr/bin/env python3
"""
Submit All Categories Final
===========================
Submit all required categories together to /grade API
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

def collect_all_required_categories():
    """Collect candidates for all required categories."""
    print("📋 COLLECTING ALL REQUIRED CATEGORIES")
    print("=" * 60)
    
    search_agent = SearchAgent()
    
    # All required categories from API error message
    required_categories = {
        "biology_expert.yml": [
            "Harvard MIT Stanford biology professor PhD researcher",
            "Nature Science Cell publication molecular biology",
            "NIH NSF grant principal investigator biology"
        ],
        "anthropology.yml": [
            "anthropology professor PhD cultural researcher",
            "ethnography fieldwork anthropological research",
            "social anthropology cultural studies"
        ],
        "bankers.yml": [
            "investment banker Goldman Sachs JPMorgan",
            "commercial banker Wells Fargo Bank America",
            "private banker wealth management finance"
        ],
        "doctors_md.yml": [
            "Harvard Medical School Johns Hopkins physician",
            "board certified internal medicine attending MD",
            "family medicine primary care doctor"
        ],
        "junior_corporate_lawyer.yml": [
            "junior associate corporate lawyer law firm",
            "corporate attorney law school JD degree",
            "business law associate attorney junior"
        ],
        "mathematics_phd.yml": [
            "mathematics PhD Harvard MIT Stanford professor",
            "mathematical research analysis theorem proof",
            "pure mathematics applied mathematics PhD"
        ],
        "mechanical_engineers.yml": [
            "mechanical engineer aerospace automotive design",
            "mechanical engineering degree BSME MSME",
            "mechanical design engineer manufacturing"
        ],
        "quantitative_finance.yml": [
            "Goldman Sachs JPMorgan quantitative analyst",
            "hedge fund portfolio manager derivatives",
            "financial engineering MIT Stanford Wharton"
        ],
        "radiology.yml": [
            "radiology physician diagnostic imaging MD",
            "radiologist medical imaging hospital",
            "diagnostic radiology attending physician"
        ],
        "tax_lawyer.yml": [
            "tax attorney law firm corporate taxation",
            "tax law lawyer IRS federal taxation",
            "corporate tax attorney legal practice"
        ]
    }
    
    all_config_candidates = {}
    
    for category, search_terms in required_categories.items():
        print(f"\n🎯 Category: {category}")
        candidate_ids = collect_candidates_for_category(search_agent, category, search_terms)
        
        if len(candidate_ids) >= 10:
            all_config_candidates[category] = candidate_ids[:10]
            print(f"✅ {category}: {len(all_config_candidates[category])} candidates")
        else:
            print(f"⚠️ {category}: Only {len(candidate_ids)} candidates (need 10)")
            all_config_candidates[category] = candidate_ids
    
    return all_config_candidates

def submit_all_to_grade_api(config_candidates, user_email):
    """Submit all categories to /grade API."""
    print("\n📤 SUBMITTING ALL CATEGORIES TO /GRADE API")
    print("=" * 60)
    
    # Filter to only include categories with exactly 10 candidates
    valid_config_candidates = {}
    for category, candidates in config_candidates.items():
        if len(candidates) == 10:
            valid_config_candidates[category] = candidates
            print(f"✅ {category}: {len(candidates)} candidates")
        else:
            print(f"⚠️ {category}: {len(candidates)} candidates (need exactly 10)")
    
    print(f"\n🚀 Submitting {len(valid_config_candidates)}/{len(config_candidates)} categories")
    
    # Use the correct format: config_candidates
    payload = {
        "config_candidates": valid_config_candidates
    }
    
    grade_url = "https://mercor-dev--search-eng-interview.modal.run/grade"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": user_email
    }
    
    try:
        print("📡 Making request to /grade API...")
        print(f"📋 Payload contains {len(valid_config_candidates)} categories")
        
        response = requests.post(
            grade_url,
            json=payload,
            headers=headers,
            timeout=300  # 5 minutes timeout for large request
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 SUCCESS! Grade API Response:")
            
            # Pretty print the response
            if 'results' in result:
                print("\n📊 FINAL SCORES:")
                above_30_count = 0
                total_score = 0
                
                for category, data in result['results'].items():
                    score = data.get('average_final_score', 'N/A')
                    status = "✅" if score >= 30.0 else "❌"
                    if score >= 30.0:
                        above_30_count += 1
                    total_score += score if isinstance(score, (int, float)) else 0
                    print(f"   {status} {category}: {score}")
                
                avg_score = total_score / len(result['results']) if result['results'] else 0
                
                print(f"\n🎯 SUMMARY:")
                print(f"   Categories above 30: {above_30_count}/{len(result['results'])}")
                print(f"   Success rate: {(above_30_count/len(result['results']))*100:.1f}%")
                print(f"   Average score: {avg_score:.2f}")
                
                if above_30_count >= 7:  # 70% success rate
                    print("🎉 EXCELLENT PERFORMANCE!")
                elif above_30_count >= 5:
                    print("🎊 GOOD PERFORMANCE!")
                else:
                    print("📈 ROOM FOR IMPROVEMENT")
                    
            else:
                print(f"   Response: {result}")
            
            # Save the response
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            response_file = f"results/final_all_categories_grade_{timestamp}.json"
            
            with open(response_file, 'w') as f:
                json.dump({
                    "timestamp": timestamp,
                    "submitted_categories": len(valid_config_candidates),
                    "total_candidates": sum(len(candidates) for candidates in valid_config_candidates.values()),
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
    print("🎓 FINAL ALL CATEGORIES GRADE SUBMISSION")
    print("=" * 70)
    
    user_email = "bhaumik.tandan@gmail.com"
    print(f"👤 User: {user_email}")
    
    try:
        # Collect candidates for all required categories
        config_candidates = collect_all_required_categories()
        
        print(f"\n📊 COLLECTION SUMMARY:")
        total_with_10 = 0
        for category, candidates in config_candidates.items():
            status = "✅" if len(candidates) == 10 else "⚠️"
            if len(candidates) == 10:
                total_with_10 += 1
            print(f"   {status} {category}: {len(candidates)} candidates")
        
        print(f"\n🎯 Categories with 10 candidates: {total_with_10}/{len(config_candidates)}")
        
        # Submit to grade API
        success = submit_all_to_grade_api(config_candidates, user_email)
        
        if success:
            print("\n🏆 FINAL SUBMISSION COMPLETED!")
            print("🎊 All categories submitted to /grade API!")
        else:
            print("\n❌ Submission failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 