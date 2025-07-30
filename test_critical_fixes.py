#!/usr/bin/env python3
"""
Test Critical Fixes for Broken Categories
Tests mathematics_phd, anthropology, and doctors_md improvements.
"""

import requests
import json
import sys
import os
from typing import List, Dict

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def test_category_fix(category: str, search_service: SearchService) -> Dict:
    """Test improved configuration for a category."""
    try:
        logger.info(f"🧪 Testing fixed {category}...")
        
        # Search with improved configurations
        search_query = SearchQuery(
            query_text=category.replace("_", " ").replace(".yml", ""),
            job_category=category,
            strategy=SearchStrategy.HYBRID,
            max_candidates=100
        )
        
        candidates = search_service.search_candidates(search_query, SearchStrategy.HYBRID)
        candidate_ids = [c.id for c in candidates[:10]]
        
        logger.info(f"📊 Found {len(candidate_ids)} candidates for {category}")
        
        if candidate_ids:
            # Show sample candidates
            logger.info(f"🎯 Sample candidates for {category}:")
            for i, candidate in enumerate(candidates[:3], 1):
                logger.info(f"   {i}. {candidate.name} - {candidate.summary[:100] if candidate.summary else 'No summary'}...")
            
            # Test evaluation
            response = requests.post(
                "https://mercor-dev--search-eng-interview.modal.run/evaluate",
                headers={"Authorization": "bhaumik.tandan@gmail.com"},
                json={"config_path": category, "object_ids": candidate_ids},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                score = data.get('average_final_score', 0)
                logger.info(f"✅ {category}: {score:.2f}")
                return {
                    "category": category,
                    "score": score,
                    "candidates_found": len(candidate_ids),
                    "success": True,
                    "candidate_ids": candidate_ids
                }
            else:
                logger.error(f"❌ {category}: API Error {response.status_code}")
                return {"category": category, "score": 0, "success": False}
        else:
            logger.warning(f"⚠️ No candidates found for {category}")
            return {"category": category, "score": 0, "success": False}
            
    except Exception as e:
        logger.error(f"❌ {category}: {e}")
        return {"category": category, "score": 0, "success": False}

def main():
    """Test critical fixes."""
    
    logger.info("🚨 TESTING CRITICAL FIXES")
    logger.info("=" * 50)
    
    # Initialize search service with improved configurations
    search_service = SearchService()
    
    # Test the critical failure categories
    critical_categories = [
        "mathematics_phd.yml",
        "anthropology.yml", 
        "doctors_md.yml",
        "biology_expert.yml",
        "quantitative_finance.yml"
    ]
    
    original_scores = {
        "mathematics_phd.yml": 0.0,
        "anthropology.yml": 0.0,
        "doctors_md.yml": 8.0,
        "biology_expert.yml": 8.0,
        "quantitative_finance.yml": 8.67
    }
    
    results = []
    total_improvement = 0
    
    for category in critical_categories:
        result = test_category_fix(category, search_service)
        results.append(result)
        
        if result["success"]:
            old_score = original_scores.get(category, 0)
            improvement = result["score"] - old_score
            total_improvement += improvement
            logger.info(f"   📈 Improvement: {old_score} → {result['score']:.2f} (+{improvement:.2f})")
        
        logger.info("")  # Blank line for readability
    
    logger.info("🏆 CRITICAL FIXES SUMMARY")
    logger.info("=" * 50)
    
    successful_fixes = 0
    for result in results:
        if result["success"]:
            category_name = result["category"].replace(".yml", "")
            old_score = original_scores.get(result["category"], 0)
            new_score = result["score"]
            improvement = new_score - old_score
            
            status = "🚀 BREAKTHROUGH" if old_score == 0 and new_score > 0 else "✅ IMPROVED" if improvement > 0 else "⚠️ MIXED"
            
            logger.info(f"{status} {category_name:<20}: {old_score:>5.1f} → {new_score:>5.1f} (+{improvement:>4.1f})")
            successful_fixes += 1
    
    logger.info(f"\n📊 RESULTS:")
    logger.info(f"   Categories Fixed: {successful_fixes}/{len(critical_categories)}")
    logger.info(f"   Total Improvement: +{total_improvement:.1f} points")
    logger.info(f"   Average per Category: +{total_improvement/len(critical_categories):.1f} points")
    
    # Save results
    timestamp = "20250731_improved"
    results_file = f"critical_fixes_results_{timestamp}.json"
    
    fix_data = {
        "metadata": {
            "timestamp": timestamp,
            "approach": "Critical fixes for broken categories",
            "total_improvement": total_improvement,
            "successful_fixes": successful_fixes
        },
        "results": {result["category"]: result for result in results}
    }
    
    with open(results_file, 'w') as f:
        json.dump(fix_data, f, indent=2)
    
    logger.info(f"💾 Results saved to {results_file}")
    logger.info("✅ Critical fixes testing complete!")

if __name__ == "__main__":
    main() 