#!/usr/bin/env python3

import os
import sys
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy

class FinalOptimizedAgent:
    def __init__(self):
        self.search_service = SearchService()
        
        # FINAL: Ultimate search terms targeting OUTSTANDING performance
        self.search_terms = {
            "tax_lawyer.yml": [
                "tax attorney JD Harvard Yale Stanford Columbia NYU law school partner associate Big Law firm IRS tax controversy Skadden Kirkland New York DC",
                "tax lawyer JD top law school Skadden Kirkland Sullivan Cromwell tax practice corporate tax M&A tax structuring partner associate BigLaw",
                "attorney JD tax law partner associate Biglaw firm tax controversy IRS audit defense tax litigation corporate Latham Watkins New York"
            ],
            "junior_corporate_lawyer.yml": [
                "JD attorney corporate lawyer 2-4 years leading law firm M&A due diligence contract negotiation international business regulatory Skadden",
                "corporate attorney JD degree law firm M&A transactions due diligence legal documentation international regulatory compliance Kirkland Ellis",
                "lawyer attorney corporate law 2-4 years experience international law firm M&A support contract negotiations cross-border Sullivan Cromwell"
            ],
            "radiology.yml": [
                "MD radiologist India medical college MBBS physician board certified radiology residency fellowship diagnostic imaging AIIMS PGI JIPMER Delhi Mumbai",
                "radiologist physician MD degree India medical school AIIMS PGI JIPMER board certification CT MRI X-ray ultrasound nuclear medicine",
                "doctor radiologist MD India medical college MBBS radiology training diagnostic imaging nuclear medicine interventional AIIMS Delhi"
            ],
            "doctors_md.yml": [
                "MD physician doctor medical school clinical practice family medicine internal medicine primary care GP residency hospital United States",
                "physician MD medical doctor clinical practice hospital residency internal medicine family practice board certified fellowship",
                "doctor MD degree physician clinical practice medical school residency training family medicine internal medicine primary care"
            ],
            "biology_expert.yml": [
                "PhD biology molecular genetics research university professor postdoc publications Nature Science Cell journal NIH NSF grant",
                "biologist PhD research molecular biology genetics cell biology university professor NIH NSF grant publications Nature Science",
                "biology researcher PhD university molecular genetics research publications postdoctoral fellow professor academic Nature Cell Science"
            ],
            "anthropology.yml": [
                "anthropology PhD university professor research ethnography fieldwork cultural social anthropologist publications AAA conference",
                "anthropologist PhD research university professor cultural social ethnographic fieldwork publications AAA American Anthropological",
                "PhD anthropology sociology research professor university ethnographic methods cultural anthropologist academic fieldwork publications"
            ],
            "mathematics_phd.yml": [
                "mathematics PhD professor university research pure applied statistics probability theory publications arXiv tenure track",
                "mathematician PhD research university professor theoretical applied mathematics statistics publications tenure Journal AMS",
                "PhD mathematics statistics research university professor publications Journal AMS mathematical modeling analysis arXiv preprint"
            ],
            "quantitative_finance.yml": [
                "quantitative analyst MBA Wharton Stanford Harvard MIT Sloan quant finance risk modeling derivatives trading Goldman Sachs JPMorgan New York London",
                "quant developer MBA top university Goldman Sachs JPMorgan Morgan Stanley quantitative research financial engineering hedge fund Two Sigma",
                "quantitative researcher MBA finance PhD mathematics statistics risk management algorithmic trading hedge fund Two Sigma Citadel"
            ],
            "bankers.yml": [
                "investment banker MBA VP director Goldman Sachs JPMorgan Morgan Stanley healthcare M&A private equity associate Evercore Wall Street",
                "healthcare investment banking MBA associate VP Goldman JPMorgan healthcare M&A biotech pharma digital health Lazard Evercore",
                "investment banking MBA healthcare sector Goldman Sachs JPMorgan Evercore Lazard M&A advisory private equity biotech pharma"
            ],
            "mechanical_engineers.yml": [
                "mechanical engineer PE license senior principal engineer Apple Tesla SpaceX Boeing automotive aerospace design manager director Silicon Valley",
                "senior mechanical engineer PE professional engineer Fortune 500 automotive aerospace product development manager Tesla Apple",
                "principal mechanical engineer PE license engineering manager director Tesla Apple Boeing SpaceX product design automotive aerospace"
            ]
        }
    
    def optimized_search(self, category: str) -> List[str]:
        """Final optimized search with multiple strategies"""
        search_terms_list = self.search_terms[category]
        all_candidates = []
        
        for search_terms in search_terms_list:
            # Vector search (primary strategy)
            query = SearchQuery(
                query_text=search_terms,
                job_category=category,
                strategy=SearchStrategy.VECTOR_ONLY,
                max_candidates=20
            )
            candidates = self.search_service.search_candidates(query)
            all_candidates.extend([c.id for c in candidates])
            
            # Try BM25 for additional coverage
            try:
                bm25_query = SearchQuery(
                    query_text=search_terms,
                    job_category=category,
                    strategy=SearchStrategy.BM25_ONLY,
                    max_candidates=15
                )
                bm25_candidates = self.search_service.search_candidates(bm25_query)
                all_candidates.extend([c.id for c in bm25_candidates])
            except:
                pass  # Continue if BM25 fails
        
        # Deduplicate while preserving order
        unique_candidates = list(dict.fromkeys(all_candidates))
        
        # Ensure exactly 10 candidates
        while len(unique_candidates) < 10 and unique_candidates:
            unique_candidates.extend(unique_candidates[:min(5, 10-len(unique_candidates))])
            unique_candidates = list(dict.fromkeys(unique_candidates))
        
        return unique_candidates[:10]
    
    def evaluate_candidates(self, category: str, candidate_ids: List[str]) -> float:
        """Evaluate candidates using the API"""
        if not candidate_ids:
            return 0.0
            
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
                timeout=25
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('average_final_score', 0)
            return 0.0
        except Exception as e:
            print(f"   ⚠️ Evaluation failed for {category}: {e}")
            return 0.0

    def process_category(self, category: str):
        """Process a single category"""
        candidate_ids = self.optimized_search(category)
        score = self.evaluate_candidates(category, candidate_ids)
        
        return {
            'category': category,
            'candidates': candidate_ids,
            'score': score
        }

def main():
    agent = FinalOptimizedAgent()
    
    categories = list(agent.search_terms.keys())
    submission = {"config_candidates": {}}
    
    print("🏆 FINAL OPTIMIZED SEARCH AGENT")
    print("=" * 50)
    print("🚀 Ready for OUTSTANDING performance!")
    print()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(agent.process_category, categories))
    
    total_score = 0
    for result in results:
        submission["config_candidates"][result['category']] = result['candidates']
        total_score += result['score']
        print(f"✅ {result['category']}: {len(result['candidates'])} candidates, Score: {result['score']:.3f}")
    
    # Save final submission
    with open("final_submission.json", "w") as f:
        json.dump(submission, f, indent=2)
    
    avg_score = total_score / len(results)
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Average Score: {avg_score:.3f}")
    print(f"Total Categories: {len(results)}")
    print(f"📄 Submission saved: final_submission.json")
    
    # Performance assessment
    if avg_score > 40:
        print("🏆 OUTSTANDING: Score above 40! MISSION ACCOMPLISHED!")
    elif avg_score > 30:
        print("🎉 EXCELLENT: Score above 30!")
    elif avg_score > 15:
        print("✅ GOOD: Score above 15!")
    else:
        print("⚠️ NEEDS IMPROVEMENT")
    
    return submission

if __name__ == "__main__":
    main() 