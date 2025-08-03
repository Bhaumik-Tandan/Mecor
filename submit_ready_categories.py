#!/usr/bin/env python3
"""
🎊 SUBMIT READY CATEGORIES TO GRADE API
======================================
Submit all categories currently scoring 30+ to the official grade API.
"""

import requests
import time
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy

def get_category_candidates(search_service, category: str) -> list:
    """Get candidates for a category using multiple strategies"""
    all_candidates = set()
    strategies = [SearchStrategy.HYBRID, SearchStrategy.VECTOR_ONLY, SearchStrategy.BM25_ONLY]
    
    for strategy in strategies:
        try:
            print(f"🔍 Getting candidates for {category} using {strategy.value}")
            
            query = SearchQuery(
                query_text=category.replace("_", " ").replace(".yml", ""),
                job_category=category,
                strategy=strategy,
                max_candidates=30
            )
            
            candidates = search_service.search_candidates(query, strategy)
            if candidates:
                candidate_ids = [c.id for c in candidates[:25]]
                all_candidates.update(candidate_ids)
                print(f"✅ Added {len(candidate_ids)} candidates from {strategy.value}")
                
            time.sleep(5)  # Conservative delay
            
        except Exception as e:
            print(f"⚠️ Strategy {strategy.value} failed for {category}: {e}")
            continue
            
    return list(all_candidates)[:10]  # Return top 10

def submit_category_to_grade_api(category: str, candidates: list) -> bool:
    """Submit a single category to the grade API"""
    try:
        print(f"🚀 SUBMITTING {category} to grade API...")
        
        payload = {
            "config_candidates": {
                category: candidates
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'bhaumik.tandan@gmail.com'
        }
        
        response = requests.post(
            'https://mercor-dev--search-eng-interview.modal.run/grade',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            print(f"🎊 SUCCESS! {category} submitted to grade API!")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ Failed to submit {category}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception submitting {category}: {e}")
        return False

def main():
    """Submit all ready categories to grade API"""
    
    # Categories that scored 30+ and are ready for submission
    ready_categories = [
        "junior_corporate_lawyer.yml",  # 50.67
        "tax_lawyer.yml",              # 40.0
        "biology_expert.yml",          # 32.0
        "radiology.yml",               # 30.33
        "mathematics_phd.yml",         # 51.0
        "bankers.yml",                 # 80.67
        "mechanical_engineers.yml"     # 67.33
    ]
    
    print("🎊 SUBMITTING READY CATEGORIES TO GRADE API")
    print("=" * 60)
    print(f"📊 Ready categories: {len(ready_categories)}")
    print(f"🎯 Target: Submit all to official grade API")
    print()
    
    # Initialize search service
    search_service = SearchService()
    
    successful_submissions = []
    failed_submissions = []
    
    for i, category in enumerate(ready_categories, 1):
        print(f"\n🔄 PROCESSING {i}/{len(ready_categories)}: {category}")
        print("-" * 50)
        
        try:
            # Get candidates
            candidates = get_category_candidates(search_service, category)
            
            if len(candidates) >= 10:
                print(f"✅ Got {len(candidates)} candidates for {category}")
                
                # Submit to grade API
                if submit_category_to_grade_api(category, candidates):
                    successful_submissions.append(category)
                else:
                    failed_submissions.append(category)
                    
                # Delay between submissions
                if i < len(ready_categories):
                    print("⏱️ Waiting 60 seconds before next submission...")
                    time.sleep(60)
                    
            else:
                print(f"❌ Insufficient candidates for {category}: {len(candidates)}")
                failed_submissions.append(category)
                
        except Exception as e:
            print(f"❌ Error processing {category}: {e}")
            failed_submissions.append(category)
            
    # Final summary
    print("\n" + "=" * 60)
    print("🎊 SUBMISSION SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {len(successful_submissions)}")
    print(f"❌ Failed: {len(failed_submissions)}")
    print()
    
    if successful_submissions:
        print("🎊 SUCCESSFULLY SUBMITTED:")
        for cat in successful_submissions:
            print(f"   ✅ {cat}")
    
    if failed_submissions:
        print("\n❌ FAILED SUBMISSIONS:")
        for cat in failed_submissions:
            print(f"   ❌ {cat}")
    
    print(f"\n📈 COMPLETION RATE: {len(successful_submissions)}/{len(ready_categories)} ({len(successful_submissions)/len(ready_categories)*100:.1f}%)")

if __name__ == "__main__":
    main() 