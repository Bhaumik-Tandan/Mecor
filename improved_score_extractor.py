#!/usr/bin/env python3
"""
🔧 IMPROVED SCORE EXTRACTOR
===========================
Robust score extraction with multiple fallback methods.
Fixes the "Failed to get scores" issue from the optimizer.
"""

import json
from typing import Dict, Optional, Any
from src.main import SearchAgent

class ImprovedScoreExtractor:
    def __init__(self):
        self.search_agent = SearchAgent()
        
    def extract_scores_robust(self) -> Dict[str, float]:
        """Extract scores with multiple fallback methods"""
        
        print("🔧 IMPROVED SCORE EXTRACTION")
        print("=" * 40)
        
        # Method 1: Standard extraction
        try:
            print("📊 Method 1: Standard extraction...")
            result = self.search_agent.run_evaluation()
            
            if result and isinstance(result, dict):
                print(f"✅ Got result type: {type(result)}")
                print(f"📋 Result keys: {list(result.keys()) if hasattr(result, 'keys') else 'No keys'}")
                
                # Try direct scores access
                if 'scores' in result:
                    scores = result['scores']
                    print(f"✅ Found scores directly: {scores}")
                    return self._validate_scores(scores)
                    
                # Try evaluation_results access
                elif 'evaluation_results' in result:
                    print("🔍 Extracting from evaluation_results...")
                    eval_results = result['evaluation_results']
                    scores = {}
                    
                    for category, eval_result in eval_results.items():
                        if hasattr(eval_result, 'average_final_score'):
                            scores[category] = float(eval_result.average_final_score)
                        elif isinstance(eval_result, dict) and 'average_final_score' in eval_result:
                            scores[category] = float(eval_result['average_final_score'])
                    
                    if scores:
                        print(f"✅ Extracted from evaluation_results: {scores}")
                        return self._validate_scores(scores)
                
                # Try summary_stats access
                elif 'summary_stats' in result:
                    print("🔍 Checking summary_stats...")
                    print(f"Summary stats: {result['summary_stats']}")
                    
            print("⚠️ Method 1 failed - no scores found in standard locations")
            
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
        
        # Method 2: Direct evaluation service
        try:
            print("\n📊 Method 2: Direct evaluation service...")
            from src.services.evaluation_service import SafeEvaluationService
            eval_service = SafeEvaluationService()
            
            # This would require implementing direct evaluation
            print("⚠️ Method 2 requires additional implementation")
            
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
        
        # Method 3: Parse from string representation
        try:
            print("\n📊 Method 3: String parsing fallback...")
            result = self.search_agent.run_evaluation()
            
            if result:
                result_str = str(result)
                scores = self._parse_scores_from_string(result_str)
                if scores:
                    print(f"✅ Parsed from string: {scores}")
                    return self._validate_scores(scores)
                    
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
        
        print("❌ All methods failed")
        return {}
    
    def _validate_scores(self, scores: Dict[str, Any]) -> Dict[str, float]:
        """Validate and convert scores to proper format"""
        validated = {}
        
        target_categories = [
            "doctors_md.yml", "anthropology.yml", "quantitative_finance.yml",
            "tax_lawyer.yml", "junior_corporate_lawyer.yml", "biology_expert.yml",
            "radiology.yml", "mathematics_phd.yml", "bankers.yml", "mechanical_engineers.yml"
        ]
        
        for category in target_categories:
            if category in scores:
                try:
                    score = float(scores[category])
                    validated[category] = score
                    print(f"   ✅ {category}: {score:.2f}")
                except (ValueError, TypeError) as e:
                    print(f"   ❌ {category}: Invalid score {scores[category]} - {e}")
            else:
                print(f"   ⚠️ {category}: Missing")
        
        return validated
    
    def _parse_scores_from_string(self, result_str: str) -> Dict[str, float]:
        """Parse scores from string representation as fallback"""
        scores = {}
        
        # Look for average_final_score patterns
        import re
        
        # Pattern: 'category.yml': EvaluationResult(...average_final_score=XX.XX...)
        pattern = r"'([^']+\.yml)'.*?average_final_score=([0-9.]+)"
        matches = re.findall(pattern, result_str)
        
        for category, score_str in matches:
            try:
                scores[category] = float(score_str)
            except ValueError:
                continue
                
        return scores
    
    def run_diagnostic(self):
        """Run diagnostic to understand the score extraction issue"""
        print("\n🔍 DIAGNOSTIC MODE")
        print("=" * 30)
        
        try:
            result = self.search_agent.run_evaluation()
            
            print(f"📊 Result type: {type(result)}")
            print(f"📊 Result value: {result}")
            
            if hasattr(result, '__dict__'):
                print(f"📊 Result attributes: {list(result.__dict__.keys())}")
            
            if isinstance(result, dict):
                print(f"📊 Dict keys: {list(result.keys())}")
                for key, value in result.items():
                    print(f"   {key}: {type(value)} - {str(value)[:100]}...")
            
        except Exception as e:
            print(f"❌ Diagnostic failed: {e}")
            import traceback
            traceback.print_exc()

def test_score_extraction():
    """Test the improved score extraction"""
    extractor = ImprovedScoreExtractor()
    
    # Run diagnostic first
    extractor.run_diagnostic()
    
    # Try extraction
    scores = extractor.extract_scores_robust()
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"✅ Successfully extracted: {len(scores)} categories")
    
    if scores:
        print("📊 SCORES:")
        for category, score in scores.items():
            status = "✅" if score >= 30 else "❌"
            print(f"   {status} {category}: {score:.2f}")
        
        # Count categories above/below 30
        above_30 = len([s for s in scores.values() if s >= 30])
        below_30 = len([s for s in scores.values() if s < 30])
        
        print(f"\n📈 SUMMARY:")
        print(f"✅ Above 30: {above_30}")
        print(f"❌ Below 30: {below_30}")
        print(f"📊 Success rate: {above_30/len(scores)*100:.1f}%")
    else:
        print("❌ No scores extracted")

if __name__ == "__main__":
    test_score_extraction() 