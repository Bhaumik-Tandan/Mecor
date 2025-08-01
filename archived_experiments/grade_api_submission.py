#!/usr/bin/env python3
"""
Official Grade API Submission
=============================
Submit to the /grade endpoint for final grading.
Format: config_candidates with exactly 10 candidates per category.
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
from src.utils.logger import setup_logger

logger = setup_logger(
    name="grade_submission",
    level="INFO",
    log_file="logs/grade_submission.log"
)

def collect_best_candidates():
    """Collect our best 10 candidates for each category."""
    
    print("🔍 Collecting best candidates for grade submission...")
    
    # First, get fresh candidate searches
    search_agent = SearchAgent()
    
    all_candidates = {}
    
    for category in config.job_categories:
        print(f"🔍 Searching {category}...")
        
        from src.models.candidate import SearchQuery, SearchStrategy
        
        query = SearchQuery(
            query_text=category.replace("_", " ").replace(".yml", ""),
            job_category=category,
            strategy=SearchStrategy.HYBRID,
            max_candidates=50  # Get more candidates to select best 10
        )
        
        candidates = search_agent.search_service.search_candidates(query, SearchStrategy.HYBRID)
        
        if len(candidates) >= 10:
            # Take top 10 candidates based on search ranking
            top_10_ids = [c.id for c in candidates[:10]]
            all_candidates[category] = top_10_ids
            print(f"✅ {category}: Found {len(candidates)} candidates, selected top 10")
        else:
            print(f"⚠️ {category}: Only found {len(candidates)} candidates (need 10)")
            # Take what we have and fill with available candidates
            candidate_ids = [c.id for c in candidates]
            # If we need more, we'll have to use what we have
            all_candidates[category] = candidate_ids
    
    return all_candidates

def submit_to_grade_api(candidates_data):
    """Submit to the official /grade endpoint."""
    
    grade_endpoint = "https://mercor-dev--search-eng-interview.modal.run/grade"
    user_email = config.api.user_email
    
    if not user_email:
        raise ValueError("USER_EMAIL not found in environment variables")
    
    headers = {
        "Authorization": user_email,
        "Content-Type": "application/json"
    }
    
    # Prepare the payload in the required format
    payload = {
        "config_candidates": candidates_data
    }
    
    print(f"\n🚀 SUBMITTING TO GRADE API")
    print("=" * 50)
    print(f"📧 Email: {user_email}")
    print(f"🎯 Endpoint: {grade_endpoint}")
    print(f"📋 Categories: {len(candidates_data)}")
    
    # Show summary
    for category, candidate_ids in candidates_data.items():
        print(f"   📊 {category}: {len(candidate_ids)} candidates")
    
    print("=" * 50)
    
    try:
        logger.info(f"Submitting to grade API with {len(candidates_data)} categories")
        
        response = requests.post(
            grade_endpoint,
            headers=headers,
            json=payload,
            timeout=120
        )
        
        response.raise_for_status()
        
        print("✅ GRADE SUBMISSION SUCCESSFUL!")
        print(f"📊 Status Code: {response.status_code}")
        
        # Save response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response_file = f"results/grade_api_response_{timestamp}.json"
        
        response_data = {
            "timestamp": timestamp,
            "status_code": response.status_code,
            "response_text": response.text,
            "submitted_categories": list(candidates_data.keys()),
            "total_candidates": sum(len(ids) for ids in candidates_data.values())
        }
        
        try:
            response_json = response.json()
            response_data["response_json"] = response_json
            print(f"📤 Response: {response_json}")
        except:
            print(f"📤 Response: {response.text}")
        
        with open(response_file, 'w') as f:
            json.dump(response_data, f, indent=2)
        
        print(f"💾 Response saved: {response_file}")
        logger.info(f"Grade submission successful: {response.status_code}")
        
        return True, response_data
        
    except requests.RequestException as e:
        print(f"❌ GRADE SUBMISSION FAILED: {e}")
        logger.error(f"Grade submission failed: {e}")
        return False, None

def main():
    """Main grade submission process."""
    try:
        print("🏆 OFFICIAL GRADE API SUBMISSION")
        print("=" * 60)
        print("🎯 Submitting to /grade endpoint for final scoring")
        print("=" * 60)
        
        # Collect best candidates
        candidates_data = collect_best_candidates()
        
        # Validate we have the right format
        missing_categories = []
        insufficient_candidates = []
        
        for category in config.job_categories:
            if category not in candidates_data:
                missing_categories.append(category)
            elif len(candidates_data[category]) < 10:
                insufficient_candidates.append(f"{category}: {len(candidates_data[category])}/10")
        
        if missing_categories:
            print(f"❌ Missing categories: {missing_categories}")
            return
        
        if insufficient_candidates:
            print(f"⚠️ Categories with <10 candidates: {insufficient_candidates}")
            user_input = input("Continue with submission anyway? (y/n): ")
            if user_input.lower() != 'y':
                print("❌ Submission cancelled")
                return
        
        # Save submission data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        submission_file = f"results/grade_submission_data_{timestamp}.json"
        
        submission_data = {
            "timestamp": timestamp,
            "submission_type": "final_grade",
            "config_candidates": candidates_data,
            "summary": {
                "total_categories": len(candidates_data),
                "total_candidates": sum(len(ids) for ids in candidates_data.values()),
                "categories": list(candidates_data.keys())
            }
        }
        
        with open(submission_file, 'w') as f:
            json.dump(submission_data, f, indent=2)
        
        print(f"💾 Submission data saved: {submission_file}")
        
        # Submit to grade API
        success, response_data = submit_to_grade_api(candidates_data)
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 GRADE SUBMISSION COMPLETED SUCCESSFULLY!")
            print("🏆 Your solution has been submitted for final grading!")
        else:
            print("❌ Grade submission failed")
            print(f"📄 Submission data saved: {submission_file}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Submission process error: {e}")
        logger.error(f"Submission process failed: {e}")

if __name__ == "__main__":
    main() 