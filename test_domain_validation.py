#!/usr/bin/env python3
"""
Domain Validation Test
======================

Test the enhanced GPT-based domain validation to ensure:
1. Biology PhDs don't match mathematics_phd searches
2. Domain-specific matching works correctly
3. GPT validation filters out mismatches
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from src.services.search_service import search_service
from src.services.gpt_service import gpt_service

def test_specific_candidate():
    """Test the specific biology PhD candidate that was mismatched."""
    
    print("🧪 TESTING SPECIFIC CANDIDATE: 67970d138a14699f1614c6b6")
    print("=" * 60)
    
    # Create a candidate profile for the biology PhD
    biology_candidate = CandidateProfile(
        id="67970d138a14699f1614c6b6",
        name="Biology PhD Researcher",
        summary="""Senior Laboratory Scientist. Molecular biologist with expertise on Plant Biology and Food Microbiology. 
        Undertaken several basic and applied research projects both as a Post-Doctoral researcher and as a Principal 
        Investigator across four European countries. Highly experienced in numerous molecular biology techniques, 
        confocal and electron microscopes, stable transformation of eukaryotes and prokaryotes for production of 
        bio-molecules. Successfully applied for European funding to design, perform and analyse proteomic and 
        transcriptomic experiments. Supervised Bsc, Msc and PhD students and was adjunct lecturer for Plant 
        Biotechnology Course in Agricultural University of Athens. Doctorate from University Of Leicester in Botany/Plant Biology."""
    )
    
    print(f"Candidate: {biology_candidate.name}")
    print(f"Summary: {biology_candidate.summary[:200]}...")
    print()
    
    # Test domain validation for different categories
    categories_to_test = [
        "mathematics_phd.yml",
        "biology_expert.yml", 
        "radiology.yml",
        "quantitative_finance.yml"
    ]
    
    if gpt_service.is_available():
        print("🤖 GPT-based Domain Validation Results:")
        print("-" * 40)
        
        for category in categories_to_test:
            validation = gpt_service.validate_candidate_domain_fit(biology_candidate, category)
            
            score = validation["relevance_score"]
            reasoning = validation["reasoning"]
            
            if score >= 0.7:
                status = "✅ STRONG MATCH"
            elif score >= 0.5:
                status = "⚠️  MODERATE MATCH"
            elif score >= 0.3:
                status = "❌ WEAK MATCH"
            else:
                status = "🚫 NO MATCH"
            
            print(f"{category:<25} Score: {score:.2f} {status}")
            print(f"  Reasoning: {reasoning}")
            print()
    
    else:
        print("❌ GPT service not available for validation")

def test_mathematics_search():
    """Test mathematics_phd search to see if biology PhD is filtered out."""
    
    print("\n🔍 TESTING MATHEMATICS_PHD SEARCH")
    print("=" * 60)
    
    query = SearchQuery(
        query_text="professional mathematics phd",
        job_category="mathematics_phd.yml",
        strategy=SearchStrategy.HYBRID,
        max_candidates=10
    )
    
    print(f"Search Query: {query.query_text}")
    print(f"Category: {query.job_category}")
    print()
    
    # Perform search
    candidates = search_service.search_candidates(query, SearchStrategy.HYBRID)
    
    print(f"📊 Found {len(candidates)} candidates:")
    print("-" * 40)
    
    biology_phd_found = False
    for i, candidate in enumerate(candidates[:10], 1):
        print(f"{i}. {candidate.name} (ID: {candidate.id})")
        if candidate.summary:
            print(f"   Summary: {candidate.summary[:150]}...")
        
        if candidate.id == "67970d138a14699f1614c6b6":
            biology_phd_found = True
            print("   ⚠️  THIS IS THE BIOLOGY PHD - SHOULD BE FILTERED OUT!")
        print()
    
    if biology_phd_found:
        print("❌ ISSUE: Biology PhD found in mathematics search!")
        print("   The enhanced filtering may not be working correctly.")
    else:
        print("✅ SUCCESS: Biology PhD correctly filtered out of mathematics search!")
    
    return not biology_phd_found

def test_biology_search():
    """Test biology_expert search to see if biology PhD is correctly included."""
    
    print("\n🔍 TESTING BIOLOGY_EXPERT SEARCH")
    print("=" * 60)
    
    query = SearchQuery(
        query_text="professional biology expert",
        job_category="biology_expert.yml", 
        strategy=SearchStrategy.HYBRID,
        max_candidates=10
    )
    
    print(f"Search Query: {query.query_text}")
    print(f"Category: {query.job_category}")
    print()
    
    # Perform search
    candidates = search_service.search_candidates(query, SearchStrategy.HYBRID)
    
    print(f"📊 Found {len(candidates)} candidates:")
    print("-" * 40)
    
    biology_phd_found = False
    for i, candidate in enumerate(candidates[:10], 1):
        print(f"{i}. {candidate.name} (ID: {candidate.id})")
        if candidate.summary:
            print(f"   Summary: {candidate.summary[:150]}...")
        
        if candidate.id == "67970d138a14699f1614c6b6":
            biology_phd_found = True
            print("   ✅ THIS IS THE BIOLOGY PHD - CORRECTLY FOUND!")
        print()
    
    if biology_phd_found:
        print("✅ SUCCESS: Biology PhD correctly found in biology search!")
    else:
        print("⚠️  Biology PhD not found in biology search (may not be in top 10)")
    
    return biology_phd_found

def main():
    """Run all domain validation tests."""
    
    print("🔬 ENHANCED DOMAIN VALIDATION TEST")
    print("=" * 80)
    print("Testing GPT-based domain matching and filtering")
    print("Ensuring biology PhDs don't contaminate mathematics searches")
    print()
    
    # Test the specific candidate
    test_specific_candidate()
    
    # Test mathematics search (should filter OUT biology PhD)
    math_success = test_mathematics_search()
    
    # Test biology search (should INCLUDE biology PhD)  
    bio_success = test_biology_search()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 60)
    
    if gpt_service.is_available():
        print("✅ GPT service available for enhanced validation")
    else:
        print("❌ GPT service not available")
    
    if math_success:
        print("✅ Mathematics search correctly filters out biology PhD")
    else:
        print("❌ Mathematics search incorrectly includes biology PhD")
    
    if bio_success:
        print("✅ Biology search correctly includes biology PhD")  
    else:
        print("⚠️  Biology search doesn't show biology PhD in top 10")
    
    print()
    if math_success and gpt_service.is_available():
        print("🎉 DOMAIN VALIDATION WORKING CORRECTLY!")
        print("✅ Enhanced GPT filtering prevents cross-domain contamination")
    else:
        print("⚠️  Domain validation needs improvement")
        print("🔧 Consider adjusting GPT thresholds or filter criteria")

if __name__ == "__main__":
    main() 