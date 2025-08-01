#!/usr/bin/env python3
"""
Complete Final Submission
=========================
Fix categories with insufficient candidates and submit to grade API.
Target: radiology.yml (9/10) and anthropology.yml (9/10)
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
from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy
from src.utils.logger import setup_logger

logger = setup_logger(
    name="final_submission",
    level="INFO",
    log_file="logs/complete_final_submission.log"
)

def enhanced_candidate_search(category, target_count=10):
    """Enhanced search to find exactly the target number of candidates."""
    
    print(f"🔍 Enhanced search for {category} (target: {target_count})")
    
    search_agent = SearchAgent()
    all_candidates = set()  # Use set to avoid duplicates
    
    # Strategy 1: HYBRID search with higher limits
    print(f"   🔧 Strategy 1: HYBRID search")
    query1 = SearchQuery(
        query_text=category.replace("_", " ").replace(".yml", ""),
        job_category=category,
        strategy=SearchStrategy.HYBRID,
        max_candidates=100
    )
    candidates1 = search_agent.search_service.search_candidates(query1, SearchStrategy.HYBRID)
    for c in candidates1:
        all_candidates.add(c.id)
    print(f"      Found {len(candidates1)} candidates, total unique: {len(all_candidates)}")
    
    if len(all_candidates) >= target_count:
        result_ids = list(all_candidates)[:target_count]
        print(f"✅ {category}: SUCCESS with Strategy 1 - {len(result_ids)} candidates")
        return result_ids
    
    # Strategy 2: VECTOR_ONLY search
    print(f"   🔧 Strategy 2: VECTOR_ONLY search")
    query2 = SearchQuery(
        query_text=category.replace("_", " ").replace(".yml", ""),
        job_category=category,
        strategy=SearchStrategy.VECTOR_ONLY,
        max_candidates=100
    )
    candidates2 = search_agent.search_service.search_candidates(query2, SearchStrategy.VECTOR_ONLY)
    for c in candidates2:
        all_candidates.add(c.id)
    print(f"      Found {len(candidates2)} candidates, total unique: {len(all_candidates)}")
    
    if len(all_candidates) >= target_count:
        result_ids = list(all_candidates)[:target_count]
        print(f"✅ {category}: SUCCESS with Strategy 2 - {len(result_ids)} candidates")
        return result_ids
    
    # Strategy 3: BM25_ONLY search
    print(f"   🔧 Strategy 3: BM25_ONLY search")
    query3 = SearchQuery(
        query_text=category.replace("_", " ").replace(".yml", ""),
        job_category=category,
        strategy=SearchStrategy.BM25_ONLY,
        max_candidates=100
    )
    candidates3 = search_agent.search_service.search_candidates(query3, SearchStrategy.BM25_ONLY)
    for c in candidates3:
        all_candidates.add(c.id)
    print(f"      Found {len(candidates3)} candidates, total unique: {len(all_candidates)}")
    
    if len(all_candidates) >= target_count:
        result_ids = list(all_candidates)[:target_count]
        print(f"✅ {category}: SUCCESS with Strategy 3 - {len(result_ids)} candidates")
        return result_ids
    
    # Strategy 4: Broader search terms
    print(f"   🔧 Strategy 4: Broader search terms")
    broader_terms = {
        "radiology.yml": "medical imaging radiologist doctor physician",
        "anthropology.yml": "anthropologist social science researcher academic"
    }
    
    if category in broader_terms:
        query4 = SearchQuery(
            query_text=broader_terms[category],
            job_category=category,
            strategy=SearchStrategy.HYBRID,
            max_candidates=150
        )
        candidates4 = search_agent.search_service.search_candidates(query4, SearchStrategy.HYBRID)
        for c in candidates4:
            all_candidates.add(c.id)
        print(f"      Found {len(candidates4)} candidates, total unique: {len(all_candidates)}")
    
    # Return what we have
    result_ids = list(all_candidates)[:target_count] if len(all_candidates) >= target_count else list(all_candidates)
    
    if len(result_ids) >= target_count:
        print(f"✅ {category}: SUCCESS with Strategy 4 - {len(result_ids)} candidates")
    else:
        print(f"⚠️ {category}: Only found {len(result_ids)}/{target_count} candidates after all strategies")
    
    return result_ids

def collect_complete_candidates():
    """Collect exactly 10 candidates for each category."""
    
    print("🎯 Collecting complete candidate sets for final submission...")
    
    # Load previous successful data
    previous_file = "results/grade_submission_data_20250801_222115.json"
    if Path(previous_file).exists():
        with open(previous_file, 'r') as f:
            previous_data = json.load(f)
            previous_candidates = previous_data.get("config_candidates", {})
    else:
        previous_candidates = {}
    
    all_candidates = {}
    
    for category in config.job_categories:
        print(f"\n📋 Processing {category}...")
        
        # Check if we already have 10 candidates from previous run
        if category in previous_candidates and len(previous_candidates[category]) == 10:
            print(f"✅ {category}: Using previous 10 candidates")
            all_candidates[category] = previous_candidates[category]
        else:
            # Need to search for more candidates
            print(f"🔍 {category}: Searching for candidates (previous: {len(previous_candidates.get(category, []))})")
            candidates = enhanced_candidate_search(category, target_count=10)
            all_candidates[category] = candidates
            
            if len(candidates) < 10:
                print(f"❌ {category}: Still insufficient candidates ({len(candidates)}/10)")
            else:
                print(f"✅ {category}: Complete set achieved ({len(candidates)}/10)")
    
    return all_candidates

def submit_complete_grade(candidates_data):
    """Submit complete data to grade API."""
    
    grade_endpoint = "https://mercor-dev--search-eng-interview.modal.run/grade"
    user_email = config.api.user_email
    
    headers = {
        "Authorization": user_email,
        "Content-Type": "application/json"
    }
    
    payload = {
        "config_candidates": candidates_data
    }
    
    print(f"\n🚀 FINAL GRADE API SUBMISSION")
    print("=" * 60)
    print(f"📧 Email: {user_email}")
    print(f"🎯 Endpoint: {grade_endpoint}")
    print(f"📋 Categories: {len(candidates_data)}")
    
    # Validation check
    all_valid = True
    for category, candidate_ids in candidates_data.items():
        status = "✅" if len(candidate_ids) == 10 else "❌"
        print(f"   {status} {category}: {len(candidate_ids)}/10 candidates")
        if len(candidate_ids) != 10:
            all_valid = False
    
    print("=" * 60)
    
    if not all_valid:
        print("❌ VALIDATION FAILED: Not all categories have exactly 10 candidates")
        return False, None
    
    try:
        logger.info(f"Submitting complete data to grade API")
        
        response = requests.post(
            grade_endpoint,
            headers=headers,
            json=payload,
            timeout=120
        )
        
        response.raise_for_status()
        
        print("🎉 FINAL GRADE SUBMISSION SUCCESSFUL!")
        print(f"📊 Status Code: {response.status_code}")
        
        # Save response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response_file = f"results/final_grade_response_{timestamp}.json"
        
        response_data = {
            "timestamp": timestamp,
            "status_code": response.status_code,
            "response_text": response.text,
            "submitted_categories": list(candidates_data.keys()),
            "total_candidates": sum(len(ids) for ids in candidates_data.values()),
            "validation_passed": True
        }
        
        try:
            response_json = response.json()
            response_data["response_json"] = response_json
            print(f"📤 API Response: {response_json}")
        except:
            print(f"📤 API Response: {response.text}")
        
        with open(response_file, 'w') as f:
            json.dump(response_data, f, indent=2)
        
        print(f"💾 Response saved: {response_file}")
        logger.info(f"Final grade submission successful: {response.status_code}")
        
        return True, response_data
        
    except requests.RequestException as e:
        print(f"❌ FINAL SUBMISSION FAILED: {e}")
        logger.error(f"Final submission failed: {e}")
        return False, None

def main():
    """Complete final submission process."""
    try:
        print("🏆 COMPLETE FINAL SUBMISSION")
        print("=" * 80)
        print("🎯 Fixing insufficient candidates and submitting to grade API")
        print("📋 Target: radiology.yml and anthropology.yml need exactly 10 candidates")
        print("=" * 80)
        
        # Collect complete candidates
        candidates_data = collect_complete_candidates()
        
        # Save complete submission data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        submission_file = f"results/complete_grade_submission_{timestamp}.json"
        
        submission_data = {
            "timestamp": timestamp,
            "submission_type": "final_complete_grade",
            "config_candidates": candidates_data,
            "summary": {
                "total_categories": len(candidates_data),
                "total_candidates": sum(len(ids) for ids in candidates_data.values()),
                "categories": list(candidates_data.keys()),
                "validation_status": {
                    category: len(candidate_ids) == 10 
                    for category, candidate_ids in candidates_data.items()
                }
            }
        }
        
        with open(submission_file, 'w') as f:
            json.dump(submission_data, f, indent=2)
        
        print(f"\n💾 Complete submission data saved: {submission_file}")
        
        # Submit to grade API
        success, response_data = submit_complete_grade(candidates_data)
        
        print("\n" + "=" * 80)
        if success:
            print("🎉 FINAL SUBMISSION COMPLETED SUCCESSFULLY!")
            print("🏆 All categories submitted with exactly 10 candidates!")
            print("🎯 Your solution is now ready for final grading!")
        else:
            print("❌ Final submission incomplete")
            print(f"📄 Data saved for review: {submission_file}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Final submission process error: {e}")
        logger.error(f"Final submission process failed: {e}")

if __name__ == "__main__":
    main() 