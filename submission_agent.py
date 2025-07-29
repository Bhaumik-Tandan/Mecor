#!/usr/bin/env python3
"""
Submission Agent with Evaluation Integration
==========================================

Candidate search system with real-time evaluation feedback.
"""

import os
import sys
import json
import time
import requests
from typing import List, Dict, Any, Optional
from dataclasses import asdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from src.services.search_service import search_service
from src.services.gpt_service import gpt_service
from src.utils.logger import setup_logger

logger = setup_logger("ai_submission_agent_eval", level="INFO")

class SubmissionAgent:
    """Candidate search agent with evaluation endpoint integration."""
    
    def __init__(self):
        self.search_service = search_service
        self.gpt_service = gpt_service
        self.eval_endpoint = "https://mercor-dev--search-eng-interview.modal.run/evaluate"
        self.user_email = config.api.user_email
        
        logger.info("Submission Agent initialized")
        logger.info(f"GPT Available: {self.gpt_service.is_available()}")
        logger.info(f"User Email: {self.user_email}")
    
    def call_evaluation_endpoint(self, config_path: str, candidate_ids: List[str]) -> Dict[str, Any]:
        """Call Mercor evaluation endpoint."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.user_email
        }
        
        payload = {
            "config_path": config_path,
            "object_ids": candidate_ids[:10]  # Max 10 candidates
        }
        
        try:
            logger.info(f"Evaluating {len(candidate_ids)} candidates for {config_path}")
            response = requests.post(self.eval_endpoint, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Evaluation score: {result.get('overallScore', 'N/A')}")
                return result
            else:
                logger.error(f"Evaluation failed: {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}", "overallScore": 0.0}
                
        except Exception as e:
            logger.error(f"Evaluation endpoint error: {e}")
            return {"error": str(e), "overallScore": 0.0}
    
    def search_with_criteria(self, category: str, max_candidates: int = 50) -> List[CandidateProfile]:
        """Search candidates using multiple strategies."""
        logger.info(f"Searching {category} with multiple strategies...")
        
        strategies_to_try = [
            (SearchStrategy.HYBRID, "Hybrid"),
            (SearchStrategy.VECTOR_ONLY, "Vector"),
            (SearchStrategy.BM25_ONLY, "BM25")
        ]
        
        all_candidates = []
        
        for strategy, strategy_name in strategies_to_try:
            logger.info(f"Trying {strategy_name} strategy...")
            
            query = SearchQuery(
                query_text=f"expert professional {category.replace('_', ' ').replace('.yml', '')}",
                job_category=category,
                strategy=strategy,
                max_candidates=max_candidates
            )
            
            candidates = self.search_service.search_candidates(query, strategy)
            
            for candidate in candidates:
                candidate.search_strategy = strategy_name
                
            all_candidates.extend(candidates)
            logger.info(f"Found {len(candidates)} candidates")
        
        # Remove duplicates
        seen_ids = set()
        unique_candidates = []
        for candidate in all_candidates:
            if candidate.id not in seen_ids:
                seen_ids.add(candidate.id)
                unique_candidates.append(candidate)
        
        logger.info(f"Total unique candidates: {len(unique_candidates)}")
        return unique_candidates[:max_candidates]
    
    def iterative_improvement(
        self, 
        category: str, 
        initial_candidates: List[CandidateProfile],
        target_score: float = 0.8,
        max_iterations: int = 3
    ) -> tuple[List[CandidateProfile], Dict[str, Any]]:
        """Improve candidate selection using evaluation feedback."""
        logger.info(f"Starting iterative improvement for {category} (target: {target_score})")
        
        best_candidates = initial_candidates[:10]
        best_evaluation = {"overallScore": 0.0}
        
        for iteration in range(max_iterations):
            logger.info(f"Iteration {iteration + 1}/{max_iterations}")
            
            candidate_ids = [c.id for c in best_candidates[:10]]
            evaluation = self.call_evaluation_endpoint(category, candidate_ids)
            
            current_score = evaluation.get("overallScore", 0.0)
            
            if current_score > best_evaluation.get("overallScore", 0.0):
                best_evaluation = evaluation
                logger.info(f"New best score: {current_score:.3f}")
            
            if current_score >= target_score:
                logger.info(f"Target score reached: {current_score:.3f}")
                break
            
            if iteration < max_iterations - 1:
                logger.info(f"Score {current_score:.3f} below target, trying variations...")
                
                for top_k in [15, 20, 25]:
                    if len(initial_candidates) >= top_k:
                        test_candidates = initial_candidates[:top_k]
                        test_ids = [c.id for c in test_candidates[:10]]
                        test_eval = self.call_evaluation_endpoint(category, test_ids)
                        
                        test_score = test_eval.get("overallScore", 0.0)
                        if test_score > best_evaluation.get("overallScore", 0.0):
                            best_candidates = test_candidates[:10]
                            best_evaluation = test_eval
                            logger.info(f"Improved with top-{top_k}: {test_score:.3f}")
        
        final_score = best_evaluation.get("overallScore", 0.0)
        logger.info(f"Final score for {category}: {final_score:.3f}")
        
        return best_candidates, best_evaluation
    
    def generate_validated_submission_with_eval(self) -> Dict[str, Any]:
        """Generate final submission using evaluation endpoint for validation."""
        logger.info("GENERATING VALIDATED SUBMISSION WITH EVALUATION")
        logger.info("=" * 50)
        
        categories = [
            "tax_lawyer.yml",
            "junior_corporate_lawyer.yml", 
            "radiology.yml",
            "doctors_md.yml",
            "biology_expert.yml",
            "anthropology.yml",
            "mathematics_phd.yml",
            "quantitative_finance.yml",
            "bankers.yml",
            "mechanical_engineers.yml"
        ]
        
        submission_data = {}
        evaluation_metadata = {}
        overall_scores = []
        
        for category in categories:
            logger.info(f"Processing: {category}")
            
            candidates = self.search_with_criteria(category, max_candidates=50)
            
            if len(candidates) < 10:
                logger.warning(f"Only found {len(candidates)} candidates")
                while len(candidates) < 10 and candidates:
                    candidates.extend(candidates[:10-len(candidates)])
            
            best_candidates, evaluation_result = self.iterative_improvement(
                category, candidates, target_score=0.8, max_iterations=3
            )
            
            final_candidate_ids = [c.id for c in best_candidates[:10]]
            
            while len(final_candidate_ids) < 10:
                final_candidate_ids.extend(final_candidate_ids[:10-len(final_candidate_ids)])
            
            submission_data[category] = final_candidate_ids[:10]
            evaluation_metadata[category] = evaluation_result
            
            score = evaluation_result.get("overallScore", 0.0)
            overall_scores.append(score)
            
            logger.info(f"Final: {len(final_candidate_ids)} candidates, score: {score:.3f}")
        
        # Calculate overall quality
        avg_evaluation_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        
        return {
            "config_candidates": submission_data,
            "evaluation_metadata": {
                "overall_evaluation_score": avg_evaluation_score,
                "categories_processed": len(categories),
                "evaluation_endpoint_used": True,
                "category_details": evaluation_metadata,
                "generation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

def main():
    """Main execution function."""
    
    print("SUBMISSION AGENT WITH EVALUATION")
    print("=" * 40)
    print("Using evaluation endpoint for candidate optimization")
    print()
    
    # Initialize agent
    agent = SubmissionAgent()
    
    # Generate submission with evaluation feedback
    start_time = time.time()
    submission_result = agent.generate_validated_submission_with_eval()
    duration = time.time() - start_time
    
    # Extract submission and metadata
    submission = {"config_candidates": submission_result["config_candidates"]}
    metadata = submission_result["evaluation_metadata"]
    
    # Save submission file
    with open("final_submission.json", "w") as f:
        json.dump(submission, f, indent=2)
    
    # Save detailed metadata
    with open("evaluation_validation_report.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Display results
    total_candidates = sum(len(ids) for ids in submission["config_candidates"].values())
    avg_score = metadata["overall_evaluation_score"]
    
    print(f"\nSUBMISSION COMPLETED!")
    print(f"Submission file: final_submission.json")
    print(f"Categories: {len(submission['config_candidates'])}")
    print(f"Total candidates: {total_candidates}")
    print(f"Evaluation endpoint: Used for validation")
    print(f"Average evaluation score: {avg_score:.3f}")
    print(f"Duration: {duration:.1f}s")
    
    # Quality assessment based on actual evaluation scores
    if avg_score >= 0.9:
        quality = "EXCELLENT"
    elif avg_score >= 0.8:
        quality = "GOOD"
    elif avg_score >= 0.7:
        quality = "FAIR"
    else:
        quality = "NEEDS IMPROVEMENT"
    
    print(f"Overall Quality: {quality}")
    
    # Show category scores
    print(f"\nCategory Evaluation Scores:")
    for category, details in metadata["category_details"].items():
        score = details.get("overallScore", 0.0)
        print(f"  {category}: {score:.3f}")
    
    if total_candidates == 100:
        print("\nSubmission format validated: Exactly 100 candidates")
        print(f"\nREADY FOR MERCOR FINAL SUBMISSION!")
        print(f"curl -H 'Authorization: {config.api.user_email}' \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d @final_submission.json \\")
        print(f"     'https://mercor-dev--search-eng-interview.modal.run/grade'")
    else:
        print(f"Warning: Expected 100 candidates, got {total_candidates}")
    
    print(f"\nDetailed evaluation report: evaluation_validation_report.json")

if __name__ == "__main__":
    main() 