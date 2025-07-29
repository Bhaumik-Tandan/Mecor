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

class CriteriaBasedAgent:
    def __init__(self):
        self.search_service = SearchService()
        
        self.evaluation_criteria = {
            "tax_lawyer.yml": {
                "hard": ["JD degree", "accredited U.S. law school", "3+ years legal practice"],
                "soft": ["corporate tax structuring", "IRS audits", "legal opinions", "federal tax code"],
                "search_terms": ["JD attorney tax lawyer law school 3 years practice IRS audit corporate tax structuring legal opinions federal tax compliance"]
            },
            "junior_corporate_lawyer.yml": {
                "hard": ["2-4 years corporate lawyer", "leading law firm", "USA Europe Canada", "reputed law school"],
                "soft": ["M&A transactions", "due diligence", "contract negotiations", "international business law"],
                "search_terms": ["JD attorney corporate lawyer 2-4 years law firm M&A due diligence contract negotiation international business regulatory compliance"]
            },
            "radiology.yml": {
                "hard": ["MD degree", "medical school U.S. or India"],
                "soft": ["board certification ABR FRCR", "3+ years experience", "CT MRI X-ray ultrasound", "AI medical imaging"],
                "search_terms": ["MD radiologist physician medical school board certified ABR FRCR CT MRI X-ray ultrasound diagnostic imaging AI applications 3 years experience"]
            },
            "doctors_md.yml": {
                "hard": ["MD degree top U.S. medical school", "2+ years clinical practice U.S.", "General Practitioner GP"],
                "soft": ["EHR systems", "telemedicine", "outpatient diagnostics", "chronic care management"],
                "search_terms": ["MD physician medical school clinical practice general practitioner GP primary care family medicine EHR telemedicine outpatient chronic care 2 years experience"]
            },
            "biology_expert.yml": {
                "hard": ["undergraduate U.S. U.K. Canada", "PhD Biology top U.S. university"],
                "soft": ["molecular biology genetics", "peer-reviewed publications", "CRISPR PCR sequencing", "experimental design"],
                "search_terms": ["PhD biology molecular genetics cell biology university research publications peer-reviewed CRISPR PCR sequencing experimental design lab techniques mentoring undergraduate"]
            },
            "anthropology.yml": {
                "hard": ["PhD sociology anthropology economics", "PhD program started within 3 years"],
                "soft": ["ethnographic methods", "fieldwork case studies", "academic publications", "migration labor technology"],
                "search_terms": ["PhD anthropology sociology economics ethnographic fieldwork cultural social migration labor academic publications conference presentations research methods 3 years program"]
            },
            "mathematics_phd.yml": {
                "hard": ["undergraduate U.S. U.K. Canada", "PhD Mathematics Statistics top U.S. university"],
                "soft": ["peer-reviewed publications", "mathematical modeling", "proof-based reasoning", "algorithmic problem-solving"],
                "search_terms": ["PhD mathematics statistics university research publications preprints mathematical modeling proof reasoning algorithmic problem solving theoretical applied undergraduate"]
            },
            "quantitative_finance.yml": {
                "hard": ["MBA Prestigious U.S. university M7", "3+ years quantitative finance", "risk modeling algorithmic trading"],
                "soft": ["portfolio optimization", "derivatives pricing", "Python QuantLib", "global investment firms"],
                "search_terms": ["MBA M7 university quantitative finance risk modeling algorithmic trading financial engineering Python QuantLib portfolio optimization derivatives 3 years experience global investment"]
            },
            "bankers.yml": {
                "hard": ["MBA U.S. university", "2+ years investment banking", "corporate finance M&A advisory"],
                "soft": ["healthcare investment banking", "private equity", "healthcare M&A", "biotech pharma services"],
                "search_terms": ["MBA investment banking M&A advisory healthcare private equity biotech pharma transactions recapitalizations growth equity diligence 2 years experience regulatory frameworks"]
            },
            "mechanical_engineers.yml": {
                "hard": ["Higher degree Mechanical Engineering", "3+ years professional experience", "mechanical design product development"],
                "soft": ["CAD tools SolidWorks AutoCAD", "ANSYS COMSOL simulation", "product lifecycle", "thermal systems fluid dynamics"],
                "search_terms": ["mechanical engineering degree professional experience CAD SolidWorks AutoCAD ANSYS COMSOL product development prototyping manufacturing thermal systems 3 years structural analysis"]
            }
        }
    
    def search_with_criteria(self, category: str) -> List[str]:
        criteria = self.evaluation_criteria[category]
        search_terms = criteria["search_terms"][0]
        
        query = SearchQuery(
            query_text=search_terms,
            job_category=category,
            strategy=SearchStrategy.VECTOR_ONLY,
            max_candidates=25
        )
        
        candidates = self.search_service.search_candidates(query)
        candidate_ids = [c.id for c in candidates]
        
        while len(candidate_ids) < 10:
            candidate_ids.extend(candidate_ids[:min(3, 10-len(candidate_ids))])
        
        return candidate_ids[:10]
    
    def evaluate_candidates(self, category: str, candidate_ids: List[str]) -> float:
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
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('average_final_score', 0)
            return 0
        except:
            return 0
    
    def process_category(self, category: str):
        candidate_ids = self.search_with_criteria(category)
        score = self.evaluate_candidates(category, candidate_ids)
        
        return {
            'category': category,
            'candidates': candidate_ids,
            'score': score,
            'hard_criteria': self.evaluation_criteria[category]["hard"],
            'soft_criteria': self.evaluation_criteria[category]["soft"]
        }

def main():
    agent = CriteriaBasedAgent()
    
    categories = list(agent.evaluation_criteria.keys())
    submission = {"config_candidates": {}}
    
    print("🎯 CRITERIA-BASED SEARCH AGENT")
    print("=" * 50)
    print("Using exact evaluation criteria from spreadsheet...")
    print()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(agent.process_category, categories))
    
    total_score = 0
    for result in results:
        submission["config_candidates"][result['category']] = result['candidates']
        total_score += result['score']
        print(f"✅ {result['category']}: {len(result['candidates'])} candidates, Score: {result['score']:.3f}")
        print(f"   Hard: {', '.join(result['hard_criteria'][:2])}")
        print(f"   Soft: {', '.join(result['soft_criteria'][:2])}")
        print()
    
    with open("final_submission.json", "w") as f:
        json.dump(submission, f, indent=2)
    
    avg_score = total_score / len(results)
    print(f"🎯 FINAL RESULTS:")
    print(f"Average Score: {avg_score:.3f}")
    print(f"Total Categories: {len(results)}")
    print(f"📄 Submission saved: final_submission.json")
    
    if avg_score > 15:
        print("🏆 EXCELLENT: Score above 15!")
    elif avg_score > 10:
        print("✅ GOOD: Score above 10!")
    else:
        print("⚠️ NEEDS IMPROVEMENT: Focus on hard criteria")
    
    return submission

if __name__ == "__main__":
    main() 