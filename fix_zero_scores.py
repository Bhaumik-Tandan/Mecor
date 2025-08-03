#!/usr/bin/env python3
"""
🔧 FIX ZERO SCORES
==================
Fix doctors_md.yml and quantitative_finance.yml showing 0 scores
"""

import json
import time
from datetime import datetime
from src.main import SearchAgent
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{timestamp} | {message}")

def test_category_evaluation(category: str):
    """Test evaluation for a specific category with detailed debugging"""
    log(f"🔧 Testing {category} evaluation...")
    
    try:
        # Create search agent
        search_agent = SearchAgent()
        
        # Test with a simple single-category evaluation
        log(f"📊 Running evaluation for {category}...")
        
        # This will run the full pipeline for just this category
        result = search_agent.run_single_category_evaluation(category)
        
        if result and 'evaluation_results' in result:
            if category in result['evaluation_results']:
                score = result['evaluation_results'][category].average_final_score
                log(f"✅ {category} score: {score:.2f}")
                return score
            else:
                log(f"❌ {category} not found in evaluation results")
                return None
        else:
            log(f"❌ {category} evaluation failed or returned no results")
            return None
            
    except Exception as e:
        log(f"❌ {category} evaluation error: {e}")
        return None

def fix_doctors_md():
    """Fix doctors_md.yml with targeted search strategy"""
    log("🏥 FIXING doctors_md.yml...")
    
    try:
        search_service = SearchService()
        
        # Try multiple targeted searches for US-trained MDs
        search_strategies = [
            "MD family medicine United States medical school",
            "American trained physician primary care US",
            "family medicine doctor US medical degree",
            "primary care physician American medical school",
            "general practitioner MD United States trained"
        ]
        
        best_score = 0
        best_strategy = None
        
        for strategy in search_strategies:
            log(f"🔍 Testing strategy: {strategy}")
            
            query = SearchQuery(
                query_text=strategy,
                job_category="doctors_md.yml",
                strategy=SearchStrategy.HYBRID
            )
            
            candidates = search_service.search_candidates(query)
            log(f"📊 Found {len(candidates)} candidates")
            
            # Quick evaluation test
            if len(candidates) >= 10:
                score = test_category_evaluation("doctors_md.yml")
                if score and score > best_score:
                    best_score = score
                    best_strategy = strategy
                    log(f"🎉 New best score: {score:.2f}")
                
                time.sleep(30)  # Rate limiting
        
        log(f"✅ doctors_md.yml best result: {best_score:.2f} with '{best_strategy}'")
        return best_score
        
    except Exception as e:
        log(f"❌ doctors_md fix error: {e}")
        return 0

def fix_quantitative_finance():
    """Fix quantitative_finance.yml with targeted search strategy"""
    log("💰 FIXING quantitative_finance.yml...")
    
    try:
        search_service = SearchService()
        
        # Try multiple targeted searches for M7 MBA + quant experience
        search_strategies = [
            "MBA quantitative analyst Harvard Wharton Stanford",
            "M7 MBA financial modeling derivatives trading",
            "top MBA quant researcher Python programming",
            "prestigious MBA quantitative finance analyst",
            "elite MBA algorithmic trading risk management"
        ]
        
        best_score = 0
        best_strategy = None
        
        for strategy in search_strategies:
            log(f"🔍 Testing strategy: {strategy}")
            
            query = SearchQuery(
                query_text=strategy,
                job_category="quantitative_finance.yml",
                strategy=SearchStrategy.HYBRID
            )
            
            candidates = search_service.search_candidates(query)
            log(f"📊 Found {len(candidates)} candidates")
            
            # Quick evaluation test
            if len(candidates) >= 10:
                score = test_category_evaluation("quantitative_finance.yml")
                if score and score > best_score:
                    best_score = score
                    best_strategy = strategy
                    log(f"🎉 New best score: {score:.2f}")
                
                time.sleep(30)  # Rate limiting
        
        log(f"✅ quantitative_finance.yml best result: {best_score:.2f} with '{best_strategy}'")
        return best_score
        
    except Exception as e:
        log(f"❌ quantitative_finance fix error: {e}")
        return 0

def get_final_scores():
    """Get comprehensive final scores"""
    log("📊 GETTING FINAL COMPREHENSIVE SCORES...")
    
    try:
        from improved_score_extractor import ImprovedScoreExtractor
        extractor = ImprovedScoreExtractor()
        scores = extractor.extract_scores_robust()
        
        if scores:
            log("✅ Final scores extracted successfully")
            above_30 = len([s for s in scores.values() if s >= 30])
            
            print(f"\n📊 FINAL SCORES SUMMARY:")
            print(f"{'='*50}")
            
            for category, score in sorted(scores.items()):
                status = "✅" if score >= 30 else "❌"
                print(f"{status} {category}: {score:.2f}")
            
            print(f"{'='*50}")
            print(f"🏆 Categories above 30: {above_30}/10 ({(above_30/10)*100:.1f}%)")
            print(f"📈 Average score: {sum(scores.values())/10:.2f}")
            
            return scores, above_30
        else:
            log("❌ Failed to extract final scores")
            return {}, 0
            
    except Exception as e:
        log(f"❌ Final score extraction error: {e}")
        return {}, 0

def main():
    """Main fix process"""
    print("🔧 FIXING ZERO SCORE ISSUES")
    print("=" * 50)
    
    log("🚀 Starting targeted fixes for 0-score categories...")
    
    # Fix doctors_md.yml
    doctors_score = fix_doctors_md()
    
    # Fix quantitative_finance.yml  
    quant_score = fix_quantitative_finance()
    
    # Get final comprehensive scores
    final_scores, categories_above_30 = get_final_scores()
    
    # Summary
    print(f"\n🎯 FIX RESULTS:")
    print(f"🏥 doctors_md.yml: → {doctors_score:.2f}")
    print(f"💰 quantitative_finance.yml: → {quant_score:.2f}")
    print(f"🏆 Total above 30: {categories_above_30}/10")
    
    if categories_above_30 == 10:
        print(f"\n🎉 SUCCESS! ALL 10 CATEGORIES ABOVE 30!")
        print(f"🎊 Ready for final submission!")
    elif categories_above_30 >= 8:
        print(f"\n✅ EXCELLENT! {categories_above_30}/10 above 30")
        print(f"📈 Major improvement achieved!")
    else:
        print(f"\n📊 Progress made, continue optimization if needed")
    
    return final_scores

if __name__ == "__main__":
    final_scores = main() 