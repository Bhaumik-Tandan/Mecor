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

class OptimizedCriteriaAgent:
    def __init__(self):
        self.search_service = SearchService()
        
        # IMPROVED: Based on comprehensive improvement plan
        self.evaluation_criteria = {
            "tax_lawyer.yml": {
                "hard": ["JD degree", "accredited U.S. law school", "3+ years legal practice"],
                "soft": ["corporate tax structuring", "IRS audits", "legal opinions", "federal tax code"],
                "search_terms": [
                    "JD attorney tax lawyer accredited law school 3 years practicing corporate tax structuring IRS audit legal opinions federal tax compliance",
                    "tax attorney JD degree U.S. law school experienced legal practice IRS representation audit defense corporate tax",
                    "attorney lawyer JD accredited law school tax specialist corporate federal tax code legal opinions IRS audit experience"
                ]
            },
            "junior_corporate_lawyer.yml": {
                "hard": ["2-4 years corporate lawyer", "leading law firm", "USA Europe Canada", "reputed law school"],
                "soft": ["M&A transactions", "due diligence", "contract negotiations", "international business law"],
                "search_terms": [
                    "JD attorney corporate lawyer 2-4 years leading law firm M&A due diligence contract negotiation international business regulatory",
                    "corporate attorney JD degree law firm M&A transactions due diligence legal documentation international regulatory compliance",
                    "lawyer attorney corporate law 2-4 years experience international law firm M&A support contract negotiations cross-border"
                ]
            },
            "radiology.yml": {
                "hard": ["MD degree", "medical school U.S. or India"],
                "soft": ["board certification ABR FRCR", "3+ years experience", "CT MRI X-ray ultrasound", "AI medical imaging"],
                "search_terms": [
                    "MD radiologist physician India medical school board certified radiology ABR FRCR CT MRI X-ray ultrasound nuclear medicine diagnostic imaging",
                    "radiologist MD degree medical school India board certification diagnostic imaging radiology residency fellowship CT scan MRI X-ray",
                    "physician radiologist MD India U.S. medical school board certified ABR FRCR diagnostic radiology CT MRI ultrasound nuclear medicine imaging"
                ]
            },
            "doctors_md.yml": {
                "hard": ["MD degree top U.S. medical school", "2+ years clinical practice U.S.", "General Practitioner GP"],
                "soft": ["EHR systems", "telemedicine", "outpatient diagnostics", "chronic care management"],
                "search_terms": [
                    "MD physician U.S. medical school clinical practice general practitioner GP primary care family medicine EHR telemedicine outpatient 2 years",
                    "physician MD degree U.S. medical school general practitioner clinical practice primary care family medicine telemedicine chronic care management",
                    "doctor physician MD U.S. trained clinical practice GP general practitioner EHR telemedicine patient education outpatient diagnostics"
                ]
            },
            "biology_expert.yml": {
                "hard": ["undergraduate U.S. U.K. Canada", "PhD Biology top U.S. university"],
                "soft": ["molecular biology genetics", "peer-reviewed publications", "CRISPR PCR sequencing", "experimental design"],
                "search_terms": [
                    "PhD biology molecular genetics cell biology U.S. university research publications peer-reviewed CRISPR PCR sequencing experimental design lab techniques",
                    "biologist PhD degree U.S. university molecular biology genetics research publications peer-reviewed CRISPR PCR sequencing mentoring undergraduate teaching",
                    "biology researcher PhD U.S. university molecular genetics cell biology experimental design publications peer-reviewed CRISPR PCR sequencing lab"
                ]
            },
            "anthropology.yml": {
                "hard": ["PhD sociology anthropology economics", "PhD program started within 3 years"],
                "soft": ["ethnographic methods", "fieldwork case studies", "academic publications", "migration labor technology"],
                "search_terms": [
                    "PhD anthropology sociology economics ethnographic fieldwork cultural social migration labor academic publications conference presentations research methods",
                    "anthropologist PhD sociology anthropology economics ethnographic methods fieldwork cultural research publications migration labor technology development",
                    "PhD student anthropology sociology economics ethnographic fieldwork case studies cultural social migration labor academic publications conference"
                ]
            },
            "mathematics_phd.yml": {
                "hard": ["undergraduate U.S. U.K. Canada", "PhD Mathematics Statistics top U.S. university"],
                "soft": ["peer-reviewed publications", "mathematical modeling", "proof-based reasoning", "algorithmic problem-solving"],
                "search_terms": [
                    "PhD mathematics statistics U.S. university research publications preprints mathematical modeling proof reasoning algorithmic problem solving theoretical applied",
                    "mathematician PhD degree U.S. university statistics research publications mathematical modeling proof-based reasoning algorithmic undergraduate teaching",
                    "PhD mathematics statistics university research theoretical applied mathematical modeling proof reasoning publications preprints algorithmic problem solving"
                ]
            },
            "quantitative_finance.yml": {
                "hard": ["MBA Prestigious U.S. university M7", "3+ years quantitative finance", "risk modeling algorithmic trading"],
                "soft": ["portfolio optimization", "derivatives pricing", "Python QuantLib", "global investment firms"],
                "search_terms": [
                    "MBA Wharton Stanford Harvard M7 university quantitative finance risk modeling algorithmic trading financial engineering Python QuantLib portfolio optimization derivatives",
                    "quantitative analyst MBA M7 Wharton Stanford Harvard Goldman Sachs Morgan Stanley risk management financial engineering portfolio optimization derivatives pricing",
                    "MBA M7 university quantitative finance 3 years risk modeling algorithmic trading derivatives pricing Python R MATLAB financial modeling global investment firm"
                ]
            },
            "bankers.yml": {
                "hard": ["MBA U.S. university", "2+ years investment banking", "corporate finance M&A advisory"],
                "soft": ["healthcare investment banking", "private equity", "healthcare M&A", "biotech pharma services"],
                "search_terms": [
                    "MBA investment banking M&A advisory healthcare private equity biotech pharma transactions recapitalizations growth equity diligence regulatory frameworks",
                    "healthcare investment banker MBA U.S. university M&A advisory private equity biotech pharma digital health growth equity fund diligence",
                    "investment banker MBA 2 years healthcare M&A private equity growth equity biotech pharma transactions recapitalizations advisory regulatory"
                ]
            },
            "mechanical_engineers.yml": {
                "hard": ["Higher degree Mechanical Engineering", "3+ years professional experience", "mechanical design product development"],
                "soft": ["CAD tools SolidWorks AutoCAD", "ANSYS COMSOL simulation", "product lifecycle", "thermal systems fluid dynamics"],
                "search_terms": [
                    "mechanical engineering degree 3 years professional experience CAD SolidWorks AutoCAD ANSYS COMSOL product development prototyping manufacturing thermal systems",
                    "mechanical engineer degree professional experience CAD tools SolidWorks AutoCAD ANSYS COMSOL simulation product development structural design thermal",
                    "engineer mechanical design product development 3 years experience CAD SolidWorks ANSYS simulation prototyping manufacturing thermal systems fluid dynamics"
                ]
            }
        }
    
    def multi_query_search(self, category: str) -> List[str]:
        """IMPROVED: Use multiple search queries per category for better coverage"""
        criteria = self.evaluation_criteria[category]
        search_terms_list = criteria["search_terms"]
        
        all_candidates = []
        for search_terms in search_terms_list:
            query = SearchQuery(
                query_text=search_terms,
                job_category=category,
                strategy=SearchStrategy.VECTOR_ONLY,
                max_candidates=15
            )
            
            candidates = self.search_service.search_candidates(query)
            candidate_ids = [c.id for c in candidates]
            all_candidates.extend(candidate_ids)
        
        # Deduplicate while preserving order
        unique_candidates = list(dict.fromkeys(all_candidates))
        
        # Ensure we have at least 10 candidates
        while len(unique_candidates) < 10 and unique_candidates:
            unique_candidates.extend(unique_candidates[:min(3, 10-len(unique_candidates))])
        
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
        """Process a single category with improved multi-query search"""
        candidate_ids = self.multi_query_search(category)
        score = self.evaluate_candidates(category, candidate_ids)
        
        return {
            'category': category,
            'candidates': candidate_ids,
            'score': score,
            'hard_criteria': self.evaluation_criteria[category]["hard"],
            'soft_criteria': self.evaluation_criteria[category]["soft"]
        }

def main():
    agent = OptimizedCriteriaAgent()
    
    categories = list(agent.evaluation_criteria.keys())
    submission = {"config_candidates": {}}
    
    print("🚀 OPTIMIZED CRITERIA-BASED SEARCH AGENT")
    print("=" * 60)
    print("🔧 IMPROVEMENTS: Multi-query search, enhanced radiology & quant finance")
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
        print("🏆 OUTSTANDING: Score above 40!")
    elif avg_score > 30:
        print("🎉 EXCELLENT: Score above 30!")
    elif avg_score > 15:
        print("✅ GOOD: Score above 15!")
    else:
        print("⚠️ NEEDS IMPROVEMENT: Focus on hard criteria")
    
    return submission

if __name__ == "__main__":
    main() 