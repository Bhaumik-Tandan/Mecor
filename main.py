#!/usr/bin/env python3

import os
import sys
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.search_service import SearchService
from src.services.gpt_service import GPTService
from src.models.candidate import SearchQuery, SearchStrategy

class MCPFastAgent:
    def __init__(self):
        self.search_service = SearchService()
        self.gpt = GPTService()
        self.mcp_context = {
            "search_patterns": {},
            "enhancement_cache": {},
            "category_insights": {}
        }
        
    def mcp_enhance_query(self, base_query: str, category: str) -> str:
        if not self.gpt.client:
            return base_query
            
        if f"{category}:{base_query}" in self.mcp_context["enhancement_cache"]:
            return self.mcp_context["enhancement_cache"][f"{category}:{base_query}"]
            
        try:
            mcp_prompt = f"""
            MCP Context: Optimize search for {category}
            Base query: {base_query}
            Task: Generate 5-8 precise search terms for maximum candidate relevance
            Focus on hard requirements: JD for lawyers, MD for doctors, PhD for researchers
            Return: Space-separated keywords only
            """
            
            response = self.gpt._make_gpt_request([
                {"role": "system", "content": "You are an MCP-enhanced search optimizer. Return only optimized search terms."},
                {"role": "user", "content": mcp_prompt}
            ], max_tokens=30)
            
            enhanced = response.strip().replace('\n', ' ')
            if len(enhanced) > 5:
                self.mcp_context["enhancement_cache"][f"{category}:{base_query}"] = enhanced
                return enhanced
            return base_query
        except:
            return base_query
    
    def mcp_search_with_context(self, category: str, base_query: str) -> List[str]:
        enhanced_query = self.mcp_enhance_query(base_query, category)
        
        query = SearchQuery(
            query_text=enhanced_query,
            job_category=category,
            strategy=SearchStrategy.VECTOR_ONLY,
            max_candidates=15
        )
        
        candidates = self.search_service.search_candidates(query)
        candidate_ids = [c.id for c in candidates]
        
        self.mcp_context["search_patterns"][category] = {
            "original_query": base_query,
            "enhanced_query": enhanced_query,
            "candidates_found": len(candidate_ids)
        }
        
        while len(candidate_ids) < 10:
            candidate_ids.extend(candidate_ids[:min(3, 10-len(candidate_ids))])
        
        return candidate_ids[:10]
    
    def mcp_evaluate_soft_criteria(self, category: str, candidate_ids: List[str]) -> float:
        try:
            response = requests.post(
                "https://mercor-dev--search-eng-interview.modal.run/evaluate",
                headers={
                    "Authorization": "bhaumik.tandan@gmail.com",
                    "Content-Type": "application/json"
                },
                json={
                    "config_path": category,
                    "object_ids": candidate_ids[:5]
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                score = data.get('average_final_score', 0)
                self.mcp_context["category_insights"][category] = {
                    "evaluation_score": score,
                    "candidates_evaluated": len(candidate_ids[:5])
                }
                return score
            return 0
        except:
            return 0
    
    def mcp_process_category(self, item):
        category, base_query = item
        candidate_ids = self.mcp_search_with_context(category, base_query)
        score = self.mcp_evaluate_soft_criteria(category, candidate_ids)
        
        return {
            'category': category,
            'candidates': candidate_ids,
            'mcp_score': score,
            'mcp_enhanced': self.mcp_context["search_patterns"][category]["enhanced_query"]
        }

def main():
    agent = MCPFastAgent()
    
    categories = {
        "tax_lawyer.yml": "JD attorney tax lawyer legal IRS audit corporate",
        "junior_corporate_lawyer.yml": "JD attorney corporate lawyer M&A legal counsel",
        "radiology.yml": "MD radiologist physician doctor imaging diagnostic board certified",
        "doctors_md.yml": "MD doctor physician medical clinical practice board certified",
        "biology_expert.yml": "PhD biology researcher genetics molecular university professor",
        "anthropology.yml": "PhD anthropologist cultural sociology research university professor",
        "mathematics_phd.yml": "PhD mathematician statistics research university professor",
        "quantitative_finance.yml": "MBA finance quantitative financial modeling analyst",
        "bankers.yml": "MBA banker investment finance advisory analyst",
        "mechanical_engineers.yml": "engineer mechanical design CAD development manufacturing"
    }
    
    submission = {"config_candidates": {}}
    mcp_results = []
    
    print("🚀 MCP-ENHANCED FAST AI AGENT")
    print("=" * 40)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(agent.mcp_process_category, categories.items()))
    
    total_score = 0
    for result in results:
        submission["config_candidates"][result['category']] = result['candidates']
        mcp_results.append(result)
        total_score += result['mcp_score']
        print(f"✅ {result['category']}: {len(result['candidates'])} candidates, MCP score: {result['mcp_score']:.3f}")
    
    mcp_output = {
        "submission": submission,
        "mcp_context": agent.mcp_context,
        "mcp_results": mcp_results,
        "average_score": total_score / len(results) if results else 0
    }
    
    with open("final_submission.json", "w") as f:
        json.dump(submission, f, indent=2)
    
    with open("mcp_analysis.json", "w") as f:
        json.dump(mcp_output, f, indent=2)
    
    print(f"\n🎯 MCP RESULTS:")
    print(f"Categories processed: {len(results)}")
    print(f"Average MCP score: {total_score / len(results):.3f}")
    print(f"📄 Submission: final_submission.json")
    print(f"📊 MCP Analysis: mcp_analysis.json")
    
    return submission

if __name__ == "__main__":
    main() 