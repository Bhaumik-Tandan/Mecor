#!/usr/bin/env python3
"""
📤 FINAL SUBMISSION TO GRADE API
===============================
Submit current results: 7/10 categories above 30
Using bhaumik.tandan@gmail.com
"""

import json
import requests
import time
from datetime import datetime
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy

# CORRECT EMAIL FOR SUBMISSION
USER_EMAIL = "bhaumik.tandan@gmail.com"

# CURRENT SCORES (7/10 above 30!)
CURRENT_SCORES = {
    "bankers.yml": 54.00,                    # ✅
    "biology_expert.yml": 32.00,             # ✅  
    "junior_corporate_lawyer.yml": 50.67,    # ✅
    "mathematics_phd.yml": 51.00,            # ✅
    "mechanical_engineers.yml": 69.00,       # ✅
    "radiology.yml": 30.33,                  # ✅
    "tax_lawyer.yml": 46.67,                 # ✅
    "anthropology.yml": 17.33,               # ❌ Need to improve
    "doctors_md.yml": 16.00,                 # ❌ Need to improve  
    "quantitative_finance.yml": 0.00         # ❌ Need to fix
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
    log("🎊 SUBMITTING 7/10 EXCELLENT RESULTS TO GRADE API...")
    log(f"📧 Using email: {USER_EMAIL}")
    
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
            
            # Submit to grade API with correct email
            response = requests.post(
                "https://mercor-dev--search-eng-interview.modal.run/grade",
                json={"config_candidates": config_candidates},
                headers={"Authorization": USER_EMAIL},
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

def save_submission_results():
    """Save submission results"""
    log("📊 SAVING SUBMISSION RESULTS...")
    
    above_30 = len([s for s in CURRENT_SCORES.values() if s >= 30])
    total_score = sum(CURRENT_SCORES.values())
    
    results = {
        "submission_time": datetime.now().isoformat(),
        "submission_email": USER_EMAIL,
        "submission_endpoint": "https://mercor-dev--search-eng-interview.modal.run/grade",
        "submission_type": "Final Submission - 7/10 Above 30",
        "reference_url": "https://mercor.notion.site/Search-Engineer-Take-Home-23e5392cc93e801fb91ff6c6c3cf995e",
        "summary": {
            "categories_above_30": above_30,
            "total_categories": 10,
            "success_rate": f"{(above_30/10)*100:.1f}%",
            "average_score": f"{total_score/10:.2f}"
        },
        "detailed_scores": CURRENT_SCORES,
        "excellent_categories": {
            "mechanical_engineers.yml": 69.00,
            "bankers.yml": 54.00,
            "mathematics_phd.yml": 51.00,
            "junior_corporate_lawyer.yml": 50.67,
            "tax_lawyer.yml": 46.67,
            "biology_expert.yml": 32.00,
            "radiology.yml": 30.33
        },
        "needs_improvement": {
            "anthropology.yml": 17.33,
            "doctors_md.yml": 16.00,
            "quantitative_finance.yml": 0.00
        }
    }
    
    with open('final_submission_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    log(f"✅ Results saved to final_submission_results.json")
    
    # Print summary table
    print(f"\n📊 FINAL SUBMISSION SUMMARY")
    print(f"=" * 60)
    print(f"📧 Email: {USER_EMAIL}")
    print(f"🏆 Success Rate: {above_30}/10 ({(above_30/10)*100:.1f}%)")
    print(f"📈 Average Score: {total_score/10:.2f}")
    print(f"=" * 60)
    
    for category, score in sorted(CURRENT_SCORES.items()):
        status = "✅" if score >= 30 else "❌"
        print(f"{status} {category.replace('.yml', ''):25s} {score:6.2f}")
    
    print(f"=" * 60)
    
    return results

if __name__ == "__main__":
    print("📤 FINAL SUBMISSION TO MERCOR GRADE API")
    print("=" * 60)
    print(f"📧 Submitting as: {USER_EMAIL}")
    print(f"🎯 Current Status: 7/10 categories above 30")
    print(f"📋 Reference: https://mercor.notion.site/Search-Engineer-Take-Home")
    print("=" * 60)
    
    # Save results first
    results = save_submission_results()
    
    # Submit to grade API
    success, response = submit_to_grade_api()
    
    if success:
        print(f"\n🎉 SUBMISSION COMPLETED SUCCESSFULLY!")
        print(f"✅ 7/10 categories above 30 submitted to grade API")
        print(f"📊 Excellent performance with 70% success rate!")
    else:
        print(f"\n❌ SUBMISSION ISSUES:")
        print(f"📝 Error: {response}")
        print(f"📊 Results saved locally for review")
    
    print(f"\n📋 NEXT: Continue optimizing remaining 3 categories if needed") 