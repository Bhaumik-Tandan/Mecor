#!/usr/bin/env python3
"""
🚨 EMERGENCY FINAL SUBMISSION
============================
Submit current scores immediately to grade API and prepare final deliverables.
"""

import json
import requests
import time
from datetime import datetime
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy
from src.config.settings import config

# CURRENT SCORES (as of 23:36 IST Aug 2, 2025)
CURRENT_SCORES = {
    "doctors_md.yml": 16.00,
    "anthropology.yml": 17.33, 
    "quantitative_finance.yml": 17.33,
    "tax_lawyer.yml": 29.33,
    "junior_corporate_lawyer.yml": 77.33,
    "biology_expert.yml": 32.00,
    "radiology.yml": 30.33,
    "mathematics_phd.yml": 51.00,
    "bankers.yml": 85.33,
    "mechanical_engineers.yml": 69.00
}

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{timestamp} | {message}")

def get_category_candidates(category: str, search_service: SearchService) -> list:
    """Get top 10 candidates for a category"""
    try:
        log(f"📋 Collecting candidates for {category}...")
        
        query = SearchQuery(
            query_text="professional experienced qualified expert",
            job_category=category,
            strategy=SearchStrategy.HYBRID
        )
        
        candidates = search_service.search_candidates(query)
        
        # Return top 10 candidates in required format
        top_candidates = []
        for candidate in candidates[:10]:
            # Handle both dict and CandidateProfile objects
            if hasattr(candidate, 'name'):
                # CandidateProfile object
                name = candidate.name or ""
                linkedin_id = candidate.linkedin_id or ""
                raw_data = {
                    "name": name,
                    "linkedinId": linkedin_id,
                    "summary": getattr(candidate, 'summary', ''),
                    "id": getattr(candidate, 'id', '')
                }
            else:
                # Dict object
                name = candidate.get("name", "")
                linkedin_id = candidate.get("linkedinId", "")
                raw_data = candidate
            
            top_candidates.append({
                "candidate_name": name,
                "candidate_linkedin_url": f"https://www.linkedin.com/in/{linkedin_id}",
                "raw_data": raw_data
            })
        
        log(f"✅ Got {len(top_candidates)} candidates for {category}")
        return top_candidates
        
    except Exception as e:
        log(f"❌ Error getting candidates for {category}: {e}")
        return []

def submit_to_grade_api():
    """Submit all categories to grade API"""
    log("🎊 STARTING EMERGENCY GRADE API SUBMISSION...")
    
    try:
        search_service = SearchService()
        all_categories = list(CURRENT_SCORES.keys())
        config_candidates = {}
        
        # Collect candidates for all categories
        for category in all_categories:
            candidates = get_category_candidates(category, search_service)
            if candidates:
                # Remove .yml extension for API
                clean_category = category.replace('.yml', '')
                config_candidates[clean_category] = candidates
            else:
                log(f"❌ Failed to get candidates for {category}")
        
        if len(config_candidates) == 10:
            log(f"📤 Submitting {len(config_candidates)} categories to grade API...")
            
            # Submit to grade API
            response = requests.post(
                "https://mercor-dev--search-eng-interview.modal.run/grade",
                json={"config_candidates": config_candidates},
                headers={"Authorization": config.USER_EMAIL},
                timeout=120
            )
            
            log(f"📊 Grade API Response: {response.status_code}")
            log(f"📝 Response Body: {response.text}")
            
            if response.status_code == 200:
                log("🎉 SUCCESSFULLY SUBMITTED TO GRADE API!")
                return True, response.text
            else:
                log(f"❌ Grade API failed: {response.text}")
                return False, response.text
        else:
            log(f"❌ Missing categories. Got {len(config_candidates)}, need 10")
            return False, f"Only got {len(config_candidates)} categories"
            
    except Exception as e:
        log(f"❌ Grade API submission error: {e}")
        return False, str(e)

def save_final_results():
    """Save final results table"""
    log("📊 SAVING FINAL RESULTS TABLE...")
    
    results_table = []
    above_30 = 0
    total_score = 0
    
    for category, score in CURRENT_SCORES.items():
        clean_name = category.replace('.yml', '').replace('_', ' ').title()
        status = "✅ PASS" if score >= 30 else "❌ FAIL"
        if score >= 30:
            above_30 += 1
        total_score += score
        
        results_table.append({
            "Category": clean_name,
            "Score": f"{score:.2f}",
            "Status": status
        })
    
    # Save as JSON
    final_results = {
        "submission_time": datetime.now().isoformat(),
        "deadline": "11:00 PM IST August 2, 2025",
        "summary": {
            "categories_above_30": above_30,
            "total_categories": 10,
            "success_rate": f"{(above_30/10)*100:.1f}%",
            "average_score": f"{total_score/10:.2f}"
        },
        "detailed_scores": results_table,
        "raw_scores": CURRENT_SCORES
    }
    
    with open("final_submission_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    # Print table
    print("\n📊 FINAL SUBMISSION RESULTS TABLE:")
    print("="*50)
    print(f"{'Category':<25} {'Score':<8} {'Status'}")
    print("-"*50)
    
    for item in results_table:
        print(f"{item['Category']:<25} {item['Score']:<8} {item['Status']}")
    
    print("-"*50)
    print(f"{'SUMMARY':<25} {final_results['summary']['average_score']:<8} {above_30}/10 PASS")
    print("="*50)
    
    log(f"✅ Results saved to final_submission_results.json")
    return final_results

if __name__ == "__main__":
    print("🚨 EMERGENCY FINAL SUBMISSION - DEADLINE MODE")
    print("="*60)
    
    # Save final results first
    results = save_final_results()
    
    # Submit to grade API
    success, response = submit_to_grade_api()
    
    if success:
        print("\n🎉 SUBMISSION COMPLETED SUCCESSFULLY!")
    else:
        print(f"\n❌ SUBMISSION ISSUES: {response}")
    
    print("\n📋 NEXT: Preparing GitHub repository and documentation...") 