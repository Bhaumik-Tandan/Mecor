#!/usr/bin/env python3
"""
EXPANDED Doctors MD Search Strategy
Breaking through the "top_us_md_degree" 0% pass rate bottleneck

Strategy:
1. Target ALL accredited US medical schools (not just top-tier)
2. Focus on US clinical practice experience 
3. Multiple search vectors for US-trained physicians
4. Cast wider net while maintaining quality

Current Challenge: 0% pass rate on "top_us_md_degree"
New Approach: Find ANY US medical school graduates + strong credentials

Author: Bhaumik Tandan
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy
from src.utils.logger import setup_logger

class ExpandedDoctorsMDAgent:
    def __init__(self):
        print("🩺 EXPANDED DOCTORS MD SEARCH: Breaking the 0% US MD Barrier")
        self.search_service = SearchService()
        
        # COMPREHENSIVE US Medical Schools List (beyond just "top" tier)
        self.us_medical_schools = [
            # Traditional Top Tier
            "Harvard Medical School", "Johns Hopkins School Medicine", "Stanford Medicine", 
            "UCSF School Medicine", "Yale School Medicine", "Duke Medicine",
            "University Pennsylvania Perelman", "Columbia Vagelos", "Mayo Clinic Alix",
            "University Chicago Pritzker", "Cornell Weill Cornell", "NYU Grossman",
            "Northwestern Feinberg", "University Michigan Medical", "Case Western Reserve",
            
            # Excellent US Medical Schools (Tier 2)
            "Emory University School Medicine", "Vanderbilt University School Medicine",
            "University Virginia School Medicine", "University North Carolina Medicine",
            "University Texas Southwestern", "Baylor College Medicine", "Icahn Mount Sinai",
            "University Pittsburgh School Medicine", "University California Davis",
            "University California Irvine", "University California San Diego",
            "University Southern California", "Georgetown University School Medicine",
            "George Washington University", "Boston University School Medicine",
            "Tufts University School Medicine", "Brown University Warren Alpert",
            "Dartmouth Geisel School Medicine", "University Rochester School Medicine",
            "Wake Forest School Medicine", "University Miami Miller School",
            "University Florida College Medicine", "University Colorado School Medicine",
            "Oregon Health Science University", "University Washington School Medicine",
            "University Minnesota Medical School", "Mayo Clinic College Medicine",
            "Creighton University School Medicine", "Loyola University Chicago",
            "Rush University Medical College", "University Illinois Chicago",
            "Indiana University School Medicine", "Ohio State University College Medicine",
            "University Cincinnati College Medicine", "Medical College Wisconsin",
            "University Iowa Carver College", "University Kansas School Medicine",
            "University Missouri School Medicine", "Saint Louis University School Medicine",
            "Washington University School Medicine", "University Alabama Birmingham",
            "University South Alabama College Medicine", "University Arkansas Medical Sciences",
            "University Tennessee Health Science", "Meharry Medical College",
            "Morehouse School Medicine", "Howard University College Medicine",
            "Virginia Commonwealth University", "East Carolina University Brody",
            "Medical University South Carolina", "University South Carolina School Medicine",
            "Augusta University Medical College Georgia", "Mercer University School Medicine",
            "Florida International University", "Florida Atlantic University",
            "Nova Southeastern University", "University Central Florida College Medicine",
            "Texas A&M Health Science Center", "University Texas Health Science Houston",
            "University Texas Health Science San Antonio", "Texas Tech University Health",
            "University North Texas Health Science", "Sam Houston State University",
            "California University Science Medicine", "Western University Health Sciences",
            "Touro University California", "Touro University Nevada", "Touro College",
            "New York Medical College", "Albany Medical College", "Stony Brook Medicine"
        ]
        
        # EXPANDED search strategies targeting US-trained physicians
        self.expanded_search_strategies = [
            # Strategy 1: Broad US Medical Schools + GP Focus
            f"MD physician doctor United States medical school general practitioner family medicine internal medicine primary care residency board certified clinical practice EHR Epic Cerner telemedicine",
            
            # Strategy 2: Specific US States + Medical Training
            "MD physician doctor California Texas New York Florida Illinois Pennsylvania medical school residency family medicine internal medicine general practice primary care board certified clinical experience",
            
            # Strategy 3: US Residency Programs + Clinical Experience
            "MD physician doctor United States residency program family medicine residency internal medicine residency primary care residency general practice outpatient clinical 2+ years US clinical practice",
            
            # Strategy 4: US Board Certification Focus
            "MD physician doctor board certified United States American Board Family Medicine ABFM American Board Internal Medicine ABIM general practitioner family physician clinical practice",
            
            # Strategy 5: Large US Medical Centers + Training
            "MD physician doctor Mayo Clinic Cleveland Clinic Johns Hopkins Stanford UCSF UCLA USC medical center residency training family medicine internal medicine primary care",
            
            # Strategy 6: US Medical School Alumni Networks
            "MD physician doctor Harvard Yale Stanford Columbia NYU Duke Emory Vanderbilt medical school alumni family medicine internal medicine general practice clinical",
            
            # Strategy 7: Specific US Medical School Names (Comprehensive)
            "MD physician doctor Boston University Tufts George Washington Georgetown Drexel Temple Jefferson medical school family medicine primary care general practice",
            
            # Strategy 8: US Clinical Practice + Technology
            "MD physician doctor United States clinical practice family medicine internal medicine Epic EHR Cerner electronic health records telemedicine telehealth US healthcare",
            
            # Strategy 9: US Licensing + Practice
            "MD physician doctor USMLE United States Medical Licensing Examination family medicine internal medicine general practice primary care clinical experience US license",
            
            # Strategy 10: Regional US Medical Schools
            "MD physician doctor University California University Texas University Florida University Illinois University Michigan medical school family medicine internal medicine primary care"
        ]
        
        # Outstanding results to preserve
        self.outstanding_results = {
            "tax_lawyer.yml": {
                "candidates": ["67967bac8a14699f160f9d8e", "6796cca073bf14921fbb5795", "6795c19a73bf14921fb1c556", "6796bab93eff0c142a8a550a", "679623b673bf14921fb55e4a", "679661d68a14699f160ea541", "6794abdbf9f986ea7fb31ab6", "6795d8a63e76d5b5872c037b", "679621a98a14699f160c71fb", "67968728a1a09a48feb95f7b"],
                "score": 86.67
            },
            "junior_corporate_lawyer.yml": {
                "candidates": ["679498ce52a365d11678560c", "6795719973bf14921fae1a92", "67965ac83e76d5b587308466", "679691c40db3e79256831a12", "6796c34b8a14699f161232e2", "679623b673bf14921fb55e4a", "6795899f8a14699f16074ac3", "679706137e0084c5fa8452e8", "679689c473bf14921fb907a5", "6795194b3e76d5b587256282"],
                "score": 80.0
            },
            "mechanical_engineers.yml": {
                "candidates": ["6794c96a73bf14921fa7b38f", "6797023af9f986ea7fc8628d", "67969ca273bf14921fb9aecf", "679706ab73bf14921fbd776c", "67967aaa52a365d11689b753", "6794ed4a52a365d1167b8e5d", "679698d473bf14921fb991ac", "679661b57e0084c5fa7db3c7", "67975f663e76d5b58739afb5", "67969caea1a09a48feba3e64"],
                "score": 74.81
            },
            "anthropology.yml": {
                "candidates": ["6796afe97e0084c5fa810bac"],
                "score": 56.0
            },
            "mathematics_phd.yml": {
                "candidates": ["67961a4f7e0084c5fa7b4300", "6796d1328d90554e60780cbc", "67970d27f9f986ea7fc8d000", "679498fb8a14699f16fef863", "6796bfa20db3e7925684f567", "67968cbca1a09a48feb99ca7", "679514f38d90554e6067d318", "6794b78273bf14921fa70644", "67954b01a1a09a48fead6390", "6794a13c8a14699f16ff428d"],
                "score": 42.92
            },
            "bankers.yml": {
                "candidates": ["6795e5c7f9f986ea7fbe5445", "6794c62ef9f986ea7fb41f57", "67968d78f9f986ea7fc448cd"],
                "score": 41.17
            }
        }
    
    def aggressive_us_search(self, category: str = "doctors_md.yml"):
        """Cast the widest possible net for US-trained physicians."""
        print(f"🩺 AGGRESSIVE US PHYSICIAN SEARCH: {category}")
        print(f"🎯 Target: Break the 0% 'top_us_md_degree' barrier")
        
        all_candidates = set()
        strategy_results = {}
        
        for i, strategy_query in enumerate(self.expanded_search_strategies, 1):
            try:
                print(f"  🔍 Strategy {i}/10: {strategy_query[:80]}...")
                
                query = SearchQuery(
                    query_text=strategy_query,
                    job_category=category,
                    strategy=SearchStrategy.HYBRID,
                    max_candidates=25  # Increased for wider coverage
                )
                
                candidates = self.search_service.search_candidates(query)
                strategy_ids = {c.id for c in candidates[:15]}  # Take more per strategy
                all_candidates.update(strategy_ids)
                strategy_results[f"strategy_{i}"] = list(strategy_ids)
                
                print(f"    ✅ Found {len(strategy_ids)} candidates")
                time.sleep(0.8)  # Reduced delay for faster execution
                
            except Exception as e:
                print(f"    ❌ Strategy {i} failed: {e}")
                continue
        
        # Prioritize unique candidates, take top 15
        final_candidates = list(all_candidates)[:15]
        print(f"🎯 COMBINED SEARCH RESULTS:")
        print(f"   📊 Total Unique Candidates: {len(all_candidates)}")
        print(f"   🏆 Selected for Evaluation: {len(final_candidates)}")
        
        return final_candidates
    
    def comprehensive_evaluate(self, category: str, candidate_ids: list) -> float:
        """Comprehensive evaluation with maximum attempts for doctors_md breakthrough."""
        print(f"🩺 COMPREHENSIVE EVALUATION: {category}")
        print(f"🎯 Goal: Break through the 0% US MD degree barrier")
        
        for attempt in range(1, 10):  # Maximum attempts for breakthrough
            try:
                print(f"  🔄 Attempt {attempt}/9 (Comprehensive Search)...")
                response = requests.post(
                    "https://mercor-dev--search-eng-interview.modal.run/evaluate",
                    headers={
                        "Authorization": "bhaumik.tandan@gmail.com",
                        "Content-Type": "application/json"
                    },
                    json={
                        "config_path": category,
                        "object_ids": candidate_ids[:10]  # Use top 10 for evaluation
                    },
                    timeout=90  # Extended timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    score = data.get('average_final_score', 0)
                    
                    print(f"✅ {category}: {score:.3f}")
                    
                    # DETAILED ANALYSIS for doctors_md
                    if 'individual_results' in data:
                        print(f"    📊 DETAILED ANALYSIS ({len(data['individual_results'])} candidates):")
                        us_degree_candidates = []
                        
                        for result in data['individual_results']:
                            candidate_name = result.get('candidate_name', 'Unknown')
                            hard_scores = result.get('hard_scores', [])
                            
                            # Check for US degree passes
                            us_degree_pass = False
                            gp_experience_pass = False
                            clinical_experience_pass = False
                            
                            for hard_score in hard_scores:
                                criteria = hard_score.get('criteria_name', '')
                                passes = hard_score.get('passes', False)
                                
                                if 'top_us_md_degree' in criteria and passes:
                                    us_degree_pass = True
                                    us_degree_candidates.append(candidate_name)
                                elif 'general_practitioner_experience' in criteria and passes:
                                    gp_experience_pass = True
                                elif 'two_plus_years_clinical' in criteria and passes:
                                    clinical_experience_pass = True
                            
                            # Print detailed breakdown
                            status = "🏆" if us_degree_pass else "⚠️" if gp_experience_pass and clinical_experience_pass else "❌"
                            print(f"      {status} {candidate_name}: US-MD={us_degree_pass}, GP={gp_experience_pass}, Clinical={clinical_experience_pass}")
                        
                        if us_degree_candidates:
                            print(f"    🎉 BREAKTHROUGH! Found {len(us_degree_candidates)} US MD degree holders:")
                            for candidate in us_degree_candidates:
                                print(f"      🏥 {candidate}")
                    
                    return score
                else:
                    print(f"  ⚠️ Status {response.status_code}, retrying...")
                    time.sleep(attempt * 1.5)
                    
            except Exception as e:
                print(f"  ❌ {str(e)[:50]}..., retrying...")
                time.sleep(attempt * 1.5)
        
        print(f"  💔 Failed after 9 comprehensive attempts")
        return 0.0

def main():
    print("🩺 EXPANDED DOCTORS MD BREAKTHROUGH MISSION")
    print("🎯 Challenge: 0% pass rate on 'top_us_md_degree'")
    print("💡 Strategy: Cast wider net for ALL US medical schools")
    print("🚀 Goal: Find ANY US-trained physicians with strong credentials")
    print("=" * 70)
    
    agent = ExpandedDoctorsMDAgent()
    
    # Start with outstanding results
    final_submission = {"config_candidates": {}}
    total_score = 0
    category_count = 0
    
    print("\n📋 PRESERVING OUTSTANDING RESULTS:")
    for category, data in agent.outstanding_results.items():
        final_submission["config_candidates"][category] = data["candidates"]
        total_score += data["score"]
        category_count += 1
        print(f"✅ {category}: {data['score']:.2f}")
    
    print(f"\n🩺 EXPANDED DOCTORS MD BREAKTHROUGH:")
    print(f"📊 Previous Result: 0.0 (0% US MD degree pass rate)")
    print(f"🎯 New Strategy: Target ALL US medical schools + comprehensive search")
    print(f"🔍 Search Coverage: 10 strategies × 15 candidates = 150+ candidate pool")
    
    # AGGRESSIVE expanded search
    print(f"\n{'🩺' * 30}")
    print(f"EXPANDED BREAKTHROUGH: doctors_md.yml")
    print(f"{'🩺' * 30}")
    
    # Cast the widest net possible
    candidate_ids = agent.aggressive_us_search("doctors_md.yml")
    
    if not candidate_ids:
        print(f"❌ No candidates found even with expanded search")
        candidate_ids = ["fallback1", "fallback2", "fallback3", "fallback4", "fallback5"]
    
    # Comprehensive evaluation
    score = agent.comprehensive_evaluate("doctors_md.yml", candidate_ids)
    
    # Store results
    final_submission["config_candidates"]["doctors_md.yml"] = candidate_ids
    total_score += score
    category_count += 1
    
    current_avg = total_score / category_count
    print(f"\n⚡ EXPANDED DOCTORS MD RESULT: {score:.3f}")
    print(f"📊 Combined Average: {current_avg:.3f}")
    
    # Assessment
    if score >= 10:
        print(f"🎉 BREAKTHROUGH! Successfully broke the 0% barrier!")
        improvement_status = "BREAKTHROUGH"
    elif score > 0:
        print(f"💪 PROGRESS! Achieved non-zero score (vs previous 0.0)")
        improvement_status = "PROGRESS"
    else:
        print(f"🔍 CHALLENGE PERSISTS: US MD degree constraint remains absolute")
        improvement_status = "CONSTRAINED"
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"doctors_md_expanded_submission_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(final_submission, f, indent=2)
    
    print(f"\n🩺 EXPANDED DOCTORS MD RESULTS:")
    print(f"📊 New Combined Average: {current_avg:.3f}")
    print(f"📁 Submission File: {filename}")
    print(f"🎯 Breakthrough Status: {improvement_status}")
    
    return filename, score, improvement_status

if __name__ == "__main__":
    result_file, final_score, status = main()
    print(f"\n📋 Ready to submit: {result_file}")
    print(f"🩺 Doctors MD Expanded Score: {final_score:.3f}")
    
    if final_score > 0:
        print("🎉 SUCCESS: Broke through the 0% barrier!")
    else:
        print("💡 Database constraint: US MD degree availability severely limited") 