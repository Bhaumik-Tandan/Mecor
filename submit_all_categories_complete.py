#!/usr/bin/env python3
"""
🎊 SUBMIT ALL CATEGORIES COMPLETE
=================================
Submit ALL 10 categories together as required by the grade API.
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
                
            time.sleep(3)  # Faster for complete submission
            
        except Exception as e:
            print(f"⚠️ Strategy {strategy.value} failed for {category}: {e}")
            continue
            
    return list(all_candidates)[:10]  # Return top 10

def submit_all_categories_to_grade_api(all_candidates: dict) -> bool:
    """Submit ALL categories to the grade API in one request"""
    try:
        print("🚀 SUBMITTING ALL CATEGORIES to grade API...")
        
        payload = {
            "config_candidates": all_candidates
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'bhaumik.tandan@gmail.com'
        }
        
        print(f"📊 Payload preview: {len(all_candidates)} categories")
        for cat, cands in all_candidates.items():
            print(f"   {cat}: {len(cands)} candidates")
        
        response = requests.post(
            'https://mercor-dev--search-eng-interview.modal.run/grade',
            headers=headers,
            json=payload,
            timeout=120
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📝 Response text: {response.text}")
        
        if response.status_code == 200:
            print("🎊 SUCCESS! ALL CATEGORIES submitted to grade API!")
            return True
        else:
            print(f"❌ Failed to submit all categories: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception submitting all categories: {e}")
        return False

def main():
    """Submit all categories to grade API"""
    
    # ALL 10 categories (both ready and needing work)
    all_categories = [
        # READY (30+)
        "junior_corporate_lawyer.yml",  # 50.67
        "tax_lawyer.yml",              # 40.0  
        "biology_expert.yml",          # 32.0
        "radiology.yml",               # 30.33
        "mathematics_phd.yml",         # 51.0
        "bankers.yml",                 # 80.67
        "mechanical_engineers.yml",    # 67.33
        
        # NEEDS WORK (below 30)
        "doctors_md.yml",              # 16.0
        "anthropology.yml",            # 17.33
        "quantitative_finance.yml"     # 17.33
    ]
    
    print("🎊 COMPLETE SUBMISSION TO GRADE API")
    print("=" * 60)
    print(f"📊 Total categories: {len(all_categories)}")
    print(f"✅ Ready (30+): 7 categories")
    print(f"⚠️ Below 30: 3 categories")
    print(f"🎯 Strategy: Submit all together as required")
    print()
    
    # Initialize search service
    search_service = SearchService()
    
    all_candidates = {}
    
    # Collect candidates for all categories
    for i, category in enumerate(all_categories, 1):
        print(f"\n🔄 COLLECTING {i}/{len(all_categories)}: {category}")
        print("-" * 50)
        
        try:
            candidates = get_category_candidates(search_service, category)
            
            if len(candidates) >= 10:
                all_candidates[category] = candidates
                print(f"✅ Collected {len(candidates)} candidates for {category}")
            else:
                print(f"⚠️ Only got {len(candidates)} candidates for {category}, using what we have")
                all_candidates[category] = candidates
                
        except Exception as e:
            print(f"❌ Error collecting candidates for {category}: {e}")
            # Use empty list as fallback
            all_candidates[category] = []
    
    print(f"\n📊 COLLECTION SUMMARY:")
    print(f"✅ Categories with candidates: {len([c for c in all_candidates.values() if c])}")
    print(f"❌ Categories without candidates: {len([c for c in all_candidates.values() if not c])}")
    
    # Submit all categories together
    if len(all_candidates) == len(all_categories):
        print(f"\n🚀 PROCEEDING WITH COMPLETE SUBMISSION...")
        
        success = submit_all_categories_to_grade_api(all_candidates)
        
        if success:
            print("\n🎊 COMPLETE SUBMISSION SUCCESSFUL!")
            print("✅ All 10 categories submitted to grade API")
        else:
            print("\n❌ COMPLETE SUBMISSION FAILED")
            print("⚠️ Check response details above")
    else:
        print(f"\n❌ INCOMPLETE DATA - Missing candidates for some categories")

if __name__ == "__main__":
    main() 