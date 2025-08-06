#!/usr/bin/env python3
"""
Private Search Evaluation Set Submission
========================================

Evaluates all categories from the Private Search Evaluation Set and submits to grade API.
"""

import sys
import os
import time
import json
import csv
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from src.services.search_service import search_service
from src.services.evaluation_service import evaluation_service
from src.utils.logger import setup_logger
from src.utils.env_loader import env_loader

# Setup logging
logger = setup_logger(
    name="private_evaluation",
    level="INFO",
    log_file="logs/private_evaluation.log"
)

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class PrivateEvaluationSubmission:
    """Private Search Evaluation Set submission system."""
    
    def __init__(self):
        self.search_service = search_service
        self.evaluation_service = evaluation_service
        self.eval_endpoint = env_loader.get('EVAL_ENDPOINT', 'https://mercor-dev--search-eng-interview.modal.run/evaluate')
        self.user_email = env_loader.get('USER_EMAIL', '')
        
        # Load categories from CSV
        self.categories = self._load_categories_from_csv()
        
        logger.info(f"🚀 Private Evaluation initialized with {len(self.categories)} categories")
    
    def _load_categories_from_csv(self) -> List[Dict[str, str]]:
        """Load categories from the Private Search Evaluation Set CSV."""
        categories = []
        
        try:
            # Read the CSV file
            csv_path = "/Users/bhaumiktandan/Downloads/Private Search Evaluation Set Final (1).csv"
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    categories.append({
                        'title': row['Title'],
                        'description': row['Natural Language Description'],
                        'hard_criteria': row['Hard Criteria'],
                        'soft_criteria': row['Soft Criteria'],
                        'yaml_file': row['Yaml File']
                    })
            
            logger.info(f"✅ Loaded {len(categories)} categories from CSV")
            return categories
            
        except Exception as e:
            logger.error(f"Failed to load categories from CSV: {e}")
            # Fallback to hardcoded categories if CSV fails
            return [
                {
                    'title': 'IP Litigation Attorney',
                    'description': 'Patent litigation attorney with a JD from a U.S. law school and over three years of experience representing clients in patent disputes.',
                    'yaml_file': 'litigation.yml'
                },
                {
                    'title': 'Environmental Scientist (PhD, Climate Modeling)',
                    'description': 'Environmental scientist with a PhD from a top U.S. university and hands-on experience using climate models to analyze environmental impacts.',
                    'yaml_file': 'environmental.yml'
                },
                {
                    'title': 'Corporate Strategy Lead (MBA, Tech)',
                    'description': 'Corporate strategy lead with an MBA from a top U.S. business school and experience developing GTM plans, pricing strategy, and competitive analyses.',
                    'yaml_file': 'corporate_lead.yml'
                },
                {
                    'title': 'AI Policy Researcher',
                    'description': 'AI policy researcher with a JD or MPP from a U.S. university and demonstrated exposure to machine learning systems.',
                    'yaml_file': 'ai_policy.yml'
                },
                {
                    'title': 'PhD Computational Chemist (Python + ML)',
                    'description': 'Computational chemist with a U.S.-based PhD and experience using Python for molecular simulation.',
                    'yaml_file': 'comp_chemist.yml'
                },
                {
                    'title': 'Staff Software Engineer (Infra Rewrite)',
                    'description': 'Staff-level backend engineer with 6+ years of experience leading infrastructure rewrites like migrating from monoliths to microservices.',
                    'yaml_file': 'infra_eng.yml'
                },
                {
                    'title': 'Robotics Engineer (Embedded + ML Control)',
                    'description': 'Robotics engineer with a U.S.-based MS or PhD and expertise in embedded systems and ML-based control.',
                    'yaml_file': 'robotics_eng.yml'
                },
                {
                    'title': 'Startup COO (Ops + Fundraising)',
                    'description': 'Startup executive with over five years of experience leading operations and managing fundraising at early-stage U.S. startups.',
                    'yaml_file': 'coo.yml'
                },
                {
                    'title': 'Algorithmic Trader (Elite Math Background)',
                    'description': 'Algorithmic trader with 2+ years of experience at a quant firm and strong mathematical pedigree.',
                    'yaml_file': 'algo_trader.yml'
                }
            ]
    
    def evaluate_all_categories(self) -> Dict[str, Any]:
        """Evaluate all categories from the Private Search Evaluation Set."""
        print(f"{Colors.BOLD}{Colors.HEADER}🔍 Private Search Evaluation Set{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.END}")
        print(f"{Colors.GREEN}📋 Evaluating {len(self.categories)} categories{Colors.END}")
        print()
        
        all_results = {}
        
        for i, category in enumerate(self.categories, 1):
            print(f"{Colors.BLUE}[{i}/{len(self.categories)}] Evaluating: {category['title']}{Colors.END}")
            
            try:
                # Search for candidates using the category description
                search_query = SearchQuery(
                    query_text=category['description'],
                    job_category=category['yaml_file'],
                    strategy=SearchStrategy.GPT_ENHANCED,
                    max_candidates=20
                )
                
                candidates = self.search_service.search_candidates(
                    search_query, 
                    SearchStrategy.GPT_ENHANCED
                )
                
                if candidates:
                    # Take top 10 candidates for evaluation
                    candidate_ids = [c.id for c in candidates[:10]]
                    
                    # Evaluate this category individually using the evaluate endpoint
                    evaluation_result = self._evaluate_single_category(category['yaml_file'], candidate_ids)
                    
                    all_results[category['yaml_file']] = {
                        'title': category['title'],
                        'candidates_found': len(candidates),
                        'candidate_ids': candidate_ids,
                        'description': category['description'],
                        'evaluation_result': evaluation_result
                    }
                    
                    print(f"{Colors.GREEN}  ✅ Found {len(candidates)} candidates{Colors.END}")
                    if evaluation_result:
                        print(f"{Colors.GREEN}  📊 Evaluation Score: {evaluation_result.get('average_final_score', 0.0):.2f}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}  ⚠️  No candidates found{Colors.END}")
                    all_results[category['yaml_file']] = {
                        'title': category['title'],
                        'candidates_found': 0,
                        'candidate_ids': [],
                        'description': category['description']
                    }
                    
            except Exception as e:
                print(f"{Colors.RED}  ❌ Error: {e}{Colors.END}")
                logger.error(f"Error evaluating {category['title']}: {e}")
                all_results[category['yaml_file']] = {
                    'title': category['title'],
                    'candidates_found': 0,
                    'candidate_ids': [],
                    'description': category['description'],
                    'error': str(e)
                }
        
        return all_results
    
    def _evaluate_single_category(self, config_name: str, candidate_ids: List[str]) -> Optional[Dict]:
        """Evaluate a single category using the evaluate endpoint."""
        if not candidate_ids:
            return None
        
        try:
            headers = {
                "Authorization": self.user_email,
                "Content-Type": "application/json"
            }
            
            payload = {
                "config_path": config_name,
                "object_ids": candidate_ids[:5]  # API accepts max 5 candidates
            }
            
            print(f"    🌐 Evaluating {config_name} with {len(candidate_ids[:5])} candidates...")
            
            response = requests.post(
                self.eval_endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"    ✅ Evaluation successful: {result.get('average_final_score', 0.0):.2f}")
                return result
            else:
                print(f"    ❌ Evaluation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"    ❌ Evaluation error: {e}")
            logger.error(f"Evaluation error for {config_name}: {e}")
            return None
    
    def submit_to_grade_api(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Submit results to the grade API."""
        print(f"\n{Colors.BOLD}📤 Submitting to Grade API{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
        
        # Prepare submission data
        submission_data = {
            "user_email": self.user_email,
            "submission_time": datetime.now().isoformat(),
            "categories": {}
        }
        
        total_score = 0
        valid_categories = 0
        
        for yaml_file, result in results.items():
            score = result.get('score', 0.0)
            submission_data["categories"][yaml_file] = {
                "title": result.get('title', ''),
                "score": score,
                "candidates_found": result.get('candidates_found', 0),
                "description": result.get('description', '')
            }
            
            if score > 0:
                total_score += score
                valid_categories += 1
        
        # Calculate average score
        avg_score = total_score / valid_categories if valid_categories > 0 else 0
        submission_data["summary"] = {
            "total_categories": len(results),
            "valid_categories": valid_categories,
            "average_score": avg_score,
            "total_score": total_score
        }
        
        print(f"{Colors.GREEN}📊 Submission Summary:{Colors.END}")
        print(f"  • Total Categories: {len(results)}")
        print(f"  • Valid Categories: {valid_categories}")
        print(f"  • Average Score: {avg_score:.2f}")
        print(f"  • Total Score: {total_score:.2f}")
        
        # Submit to API
        try:
            response = requests.post(
                self.eval_endpoint,
                json=submission_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                api_response = response.json()
                print(f"{Colors.GREEN}✅ Successfully submitted to Grade API{Colors.END}")
                print(f"{Colors.CYAN}API Response: {json.dumps(api_response, indent=2)}{Colors.END}")
                return api_response
            else:
                print(f"{Colors.RED}❌ API submission failed: {response.status_code}{Colors.END}")
                print(f"{Colors.RED}Response: {response.text}{Colors.END}")
                return {"error": f"API submission failed: {response.status_code}"}
                
        except Exception as e:
            print(f"{Colors.RED}❌ API submission error: {e}{Colors.END}")
            logger.error(f"API submission error: {e}")
            return {"error": str(e)}
    
    def save_results(self, results: Dict[str, Any], api_response: Dict[str, Any]):
        """Save results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"private_evaluation_results_{timestamp}.json"
        
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "api_response": api_response
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"{Colors.GREEN}💾 Results saved to: {filename}{Colors.END}")
    
    def display_results(self, results: Dict[str, Any]):
        """Display evaluation results."""
        print(f"\n{Colors.BOLD}📊 Evaluation Results{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.END}")
        
        # Sort by score (descending)
        sorted_results = sorted(
            results.items(), 
            key=lambda x: x[1].get('score', 0), 
            reverse=True
        )
        
        print(f"{Colors.BOLD}{'Rank':<4} {'Category':<35} {'Score':<8} {'Candidates':<12}{Colors.END}")
        print(f"{Colors.CYAN}{'-' * 80}{Colors.END}")
        
        total_score = 0
        valid_categories = 0
        
        for i, (yaml_file, result) in enumerate(sorted_results, 1):
            title = result.get('title', 'Unknown')[:34]
            score = result.get('score', 0.0)
            candidates = result.get('candidates_found', 0)
            
            if score > 0:
                total_score += score
                valid_categories += 1
                color = Colors.GREEN if score >= 30 else Colors.YELLOW
            else:
                color = Colors.RED
            
            print(f"{i:<4} {title:<35} {color}{score:<8.2f}{Colors.END} {candidates:<12}")
        
        print(f"{Colors.CYAN}{'-' * 80}{Colors.END}")
        
        avg_score = total_score / valid_categories if valid_categories > 0 else 0
        print(f"{Colors.BOLD}Summary:{Colors.END}")
        print(f"  • Total Categories: {len(results)}")
        print(f"  • Valid Categories: {valid_categories}")
        print(f"  • Average Score: {avg_score:.2f}")
        print(f"  • Categories ≥30: {sum(1 for _, r in sorted_results if r.get('score', 0) >= 30)}")
    
    def run_complete_evaluation(self):
        """Run complete evaluation and submission process."""
        print(f"{Colors.BOLD}{Colors.HEADER}🚀 Private Search Evaluation Set - Complete Process{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.END}")
        
        # Step 1: Evaluate all categories
        results = self.evaluate_all_categories()
        
        # Step 2: Display results
        self.display_results(results)
        
        # Step 3: Submit to grade API
        api_response = self.submit_to_grade_api(results)
        
        # Step 4: Save results
        self.save_results(results, api_response)
        
        print(f"\n{Colors.GREEN}🎉 Complete evaluation process finished!{Colors.END}")

def main():
    """Main function."""
    try:
        evaluator = PrivateEvaluationSubmission()
        evaluator.run_complete_evaluation()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        logger.error(f"Main function error: {e}")

if __name__ == "__main__":
    main() 