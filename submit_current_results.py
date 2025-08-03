#!/usr/bin/env python3
"""
📤 SUBMIT CURRENT RESULTS
========================
Submit current excellent results: 8/10 categories above 30
"""

import json
import requests
import time
from datetime import datetime
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy
from src.config.settings import config

# CURRENT EXCELLENT SCORES (8/10 above 30!)
CURRENT_SCORES = {
    "tax_lawyer.yml": 46.00,        # ✅ MAJOR WIN (+16.67)
    "junior_corporate_lawyer.yml": 85.33,  # ✅ 
    "radiology.yml": 30.33,         # ✅
    "doctors_md.yml": 0.00,         # ⚠️ Need to fix
    "biology_expert.yml": 32.00,    # ✅
    "anthropology.yml": 34.00,      # ✅ MAJOR WIN (+16.67)
    "mathematics_phd.yml": 51.00,   # ✅
    "quantitative_finance.yml": 0.00, # ⚠️ Need to fix
    "bankers.yml": 84.00,           # ✅
    "mechanical_engineers.yml": 35.00 # ✅
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
    log("🎊 SUBMITTING 8/10 EXCELLENT RESULTS TO GRADE API...")
    
    try:
        search_service = SearchService()
        all_categories = list(CURRENT_SCORES.keys())
        config_candidates = {}
        
        # Collect candidates for all categories (including 0-score ones)
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

def save_current_results():
    """Save current excellent results"""
    log("📊 SAVING CURRENT EXCELLENT RESULTS...")
    
    above_30 = len([s for s in CURRENT_SCORES.values() if s >= 30])
    total_score = sum(CURRENT_SCORES.values())
    
    results = {
        "submission_time": datetime.now().isoformat(),
        "submission_type": "Current Results - 8/10 Above 30",
        "major_achievements": {
            "anthropology_improvement": "17.33 → 34.00 (+16.67)",
            "tax_lawyer_improvement": "29.33 → 46.00 (+16.67)",
            "success_rate_improvement": "6/10 → 8/10 (60% → 80%)"
        },
        "summary": {
            "categories_above_30": above_30,
            "total_categories": 10,
            "success_rate": f"{(above_30/10)*100:.1f}%",
            "average_score": f"{total_score/10:.2f}"
        },
        "detailed_scores": CURRENT_SCORES,
        "issues_to_fix": {
            "doctors_md.yml": "0.00 - needs search configuration fix",
            "quantitative_finance.yml": "0.00 - needs search configuration fix"
        }
    }
    
    with open('current_submission_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    log(f"✅ Results saved to current_submission_results.json")
    
    # Print summary
    print(f"\n🎊 CURRENT SUBMISSION SUMMARY:")
    print(f"🏆 Categories above 30: {above_30}/10 ({(above_30/10)*100:.1f}%)")
    print(f"📈 Average score: {total_score/10:.2f}")
    print(f"🎉 Major wins: anthropology (+16.67), tax_lawyer (+16.67)")
    print(f"⚠️ Need fixes: doctors_md, quantitative_finance (showing 0)")
    
    return results

if __name__ == "__main__":
    print("📤 SUBMITTING CURRENT EXCELLENT RESULTS")
    print("=" * 50)
    
    # Save results
    results = save_current_results()
    
    # Submit to grade API
    success, response = submit_to_grade_api()
    
    if success:
        print("\n🎉 SUBMISSION COMPLETED SUCCESSFULLY!")
        print("✅ 8/10 categories above 30 submitted to grade API")
    else:
        print(f"\n❌ SUBMISSION ISSUES: {response}")
        print("📊 Results saved locally for review")
    
    print(f"\n📋 NEXT: Investigate 0-score issues and fix remaining 2 categories") 