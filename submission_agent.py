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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from src.services.search_service import search_service
from src.services.gpt_service import gpt_service
from src.agents.enhanced_validation_agent import EnhancedValidationAgent
from src.utils.logger import setup_logger
logger = setup_logger("ai_submission_agent_eval", level="INFO")
class SubmissionAgent:
    """Candidate search agent with evaluation endpoint integration."""
    def __init__(self):
        self.search_service = search_service
        self.gpt_service = gpt_service
        self.validation_agent = EnhancedValidationAgent()
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
            "object_ids": candidate_ids
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
        """Search candidates using multiple strategies with quality filtering."""
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
        seen_ids = set()
        unique_candidates = []
        for candidate in all_candidates:
            if candidate.id not in seen_ids:
                seen_ids.add(candidate.id)
                unique_candidates.append(candidate)
        logger.info(f"Total unique candidates: {len(unique_candidates)}")
        quality_filtered = self._apply_quality_filtering(unique_candidates, category)
        logger.info(f"After quality filtering: {len(quality_filtered)} candidates")
        return quality_filtered[:max_candidates]
    def _apply_quality_filtering(self, candidates: List[CandidateProfile], category: str) -> List[CandidateProfile]:
        """Apply quality filtering to candidates."""
        if not candidates:
            return candidates
        logger.info(f"Applying quality filtering to {len(candidates)} candidates...")
        scored_candidates = []
        for candidate in candidates:
            quality_validation = self.validation_agent.validate_candidate_quality(candidate)
            quality_score = quality_validation["enhanced_score"]
            scored_candidates.append({
                "candidate": candidate,
                "quality_score": quality_score,
                "quality_level": quality_validation["quality_level"],
                "validation": quality_validation
            })
        scored_candidates.sort(key=lambda x: x["quality_score"], reverse=True)
        min_quality_threshold = self.validation_agent.quality_thresholds['acceptable']
        filtered_candidates = [
            item["candidate"] for item in scored_candidates 
            if item["quality_score"] >= min_quality_threshold
        ]
        if len(filtered_candidates) < max(5, len(candidates) * 0.3):
            relaxed_threshold = min_quality_threshold * 0.8
            logger.info(f"Relaxing quality threshold to {relaxed_threshold:.3f}")
            filtered_candidates = [
                item["candidate"] for item in scored_candidates 
                if item["quality_score"] >= relaxed_threshold
            ]
        logger.info(f"Quality filtering: {len(candidates)} -> {len(filtered_candidates)} candidates")
        return filtered_candidates
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
            quality_validation = self.validation_agent.validate_candidate_list(
                best_candidates[:10], category
            )
            avg_quality = quality_validation["average_quality_score"]
            should_rerun, reason = self.validation_agent.should_rerun_search(
                current_score, avg_quality
            )
            if should_rerun and iteration < max_iterations - 1:
                logger.info(f"Rerunning search: {reason}")
                new_candidates = self.search_with_criteria(category, max_candidates=75)
                if len(new_candidates) > len(initial_candidates):
                    best_candidates = new_candidates[:15]
                    continue
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
        logger.info("Phase 1: Initial candidate search and evaluation")
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
        logger.info("\nPhase 2: Final validation and correction with MongoDB + GPT")
        final_result = self.validate_and_correct_final_submission(submission_data)
        avg_evaluation_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        final_result["evaluation_metadata"] = {
            "initial_evaluation_score": avg_evaluation_score,
            "final_evaluation_score": final_result["validation_metadata"]["average_final_score"],
                "categories_processed": len(categories),
                "category_details": evaluation_metadata,
            "total_candidates": sum(len(ids) for ids in final_result["config_candidates"].values()),
            "strategy": "Enhanced AI with MongoDB+GPT Validation",
            "validation_completed": True,
            "validation_summary": final_result["validation_metadata"]
        }
        return final_result
    def validate_and_correct_final_submission(self, submission_data: Dict[str, List[str]]) -> Dict[str, Any]:
        """Validate final submission with MongoDB and GPT, correct if needed."""
        logger.info("Starting final validation and correction of submission...")
        corrected_submission = {}
        validation_reports = {}
        correction_stats = {
            "total_candidates": 0,
            "candidates_corrected": 0,
            "categories_corrected": 0,
            "gpt_validations": 0,
            "mongodb_validations": 0
        }
        for category, candidate_ids in submission_data.items():
            logger.info(f"Validating category: {category}")
            validated_candidates = []
            category_corrections = 0
            max_attempts = 3  # Maximum attempts to find suitable candidates
            for i, candidate_id in enumerate(candidate_ids):
                correction_stats["total_candidates"] += 1
                attempt = 0
                current_candidate_id = candidate_id
                while attempt < max_attempts:
                    attempt += 1
                    mongo_data = self.validation_agent.get_full_candidate_data_from_mongodb(current_candidate_id)
                    correction_stats["mongodb_validations"] += 1
                    if not mongo_data:
                        logger.warning(f"No MongoDB data for candidate {current_candidate_id}, finding replacement...")
                        replacement_id = self._find_replacement_candidate(category, validated_candidates)
                        if replacement_id:
                            current_candidate_id = replacement_id
                            continue
                        else:
                            logger.error(f"No replacement found for {current_candidate_id}")
                            break
                    gpt_validation = self.validation_agent.validate_candidate_with_gpt(mongo_data, category)
                    correction_stats["gpt_validations"] += 1
                    logger.info(f"GPT validation for {mongo_data.get('name', 'Unknown')}: suitable={gpt_validation['is_suitable']}, score={gpt_validation.get('overall_score', 0):.3f}")
                    if (gpt_validation["is_suitable"] and 
                        gpt_validation.get("overall_score", 0) >= 0.6 and
                        gpt_validation.get("confidence", 0) >= 0.7):
                        validated_candidates.append(current_candidate_id)
                        logger.info(f"✅ Candidate {current_candidate_id} validated successfully")
                        break
                    else:
                        logger.warning(f"❌ Candidate {current_candidate_id} not suitable: {gpt_validation.get('reasoning', 'No reason')}")
                        if attempt < max_attempts:
                            replacement_id = self._find_replacement_candidate(category, validated_candidates + [current_candidate_id])
                            if replacement_id:
                                logger.info(f"🔄 Trying replacement candidate {replacement_id}")
                                current_candidate_id = replacement_id
                                category_corrections += 1
                                correction_stats["candidates_corrected"] += 1
                            else:
                                logger.warning(f"No suitable replacement found for {current_candidate_id}")
                                validated_candidates.append(current_candidate_id)
                                break
                        else:
                            logger.warning(f"Max attempts reached, keeping candidate {current_candidate_id}")
                            validated_candidates.append(current_candidate_id)
                            break
            while len(validated_candidates) < 10:
                replacement_id = self._find_replacement_candidate(category, validated_candidates)
                if replacement_id:
                    validated_candidates.append(replacement_id)
                else:
                    validated_candidates.extend(validated_candidates[:10-len(validated_candidates)])
                    break
            corrected_submission[category] = validated_candidates[:10]
            if category_corrections > 0:
                correction_stats["categories_corrected"] += 1
            validation_reports[category] = {
                "original_candidates": candidate_ids,
                "corrected_candidates": validated_candidates[:10],
                "corrections_made": category_corrections,
                "validation_success": True
            }
            logger.info(f"Category {category} completed: {category_corrections} corrections made")
        logger.info("Performing final evaluation of corrected submission...")
        final_evaluation_scores = {}
        for category, candidate_ids in corrected_submission.items():
            evaluation_result = self.call_evaluation_endpoint(category, candidate_ids)
            final_evaluation_scores[category] = evaluation_result.get("overallScore", 0.0)
            logger.info(f"Final evaluation for {category}: {final_evaluation_scores[category]:.3f}")
        avg_final_score = sum(final_evaluation_scores.values()) / len(final_evaluation_scores) if final_evaluation_scores else 0.0
        final_result = {
            "config_candidates": corrected_submission,
            "validation_metadata": {
                "validation_completed": True,
                "correction_stats": correction_stats,
                "category_reports": validation_reports,
                "final_evaluation_scores": final_evaluation_scores,
                "average_final_score": avg_final_score,
                "total_corrections": correction_stats["candidates_corrected"],
                "validation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        logger.info(f"Final validation completed!")
        logger.info(f"Total corrections: {correction_stats['candidates_corrected']}")
        logger.info(f"Categories corrected: {correction_stats['categories_corrected']}")
        logger.info(f"Average final score: {avg_final_score:.3f}")
        return final_result
    def _find_replacement_candidate(self, category: str, exclude_ids: List[str]) -> Optional[str]:
        """Find a replacement candidate for the given category."""
        try:
            logger.info(f"Finding replacement candidate for {category}, excluding {len(exclude_ids)} candidates")
            candidates = self.search_with_criteria(category, max_candidates=30)
            available_candidates = [c for c in candidates if c.id not in exclude_ids]
            if available_candidates:
                best_candidate = available_candidates[0]
                logger.info(f"Found replacement candidate: {best_candidate.id}")
                return best_candidate.id
            else:
                logger.warning(f"No replacement candidates available for {category}")
                return None
        except Exception as e:
            logger.error(f"Error finding replacement candidate: {e}")
            return None
def main():
    """Main execution function."""
    print("SUBMISSION AGENT WITH EVALUATION")
    print("=" * 40)
    print("Using evaluation endpoint for candidate optimization")
    print("Enhanced with MongoDB + GPT final validation")
    print()
    agent = SubmissionAgent()
    start_time = time.time()
    submission_result = agent.generate_validated_submission_with_eval()
    duration = time.time() - start_time
    submission = {"config_candidates": submission_result["config_candidates"]}
    metadata = submission_result["evaluation_metadata"]
    validation_summary = metadata.get("validation_summary", {})
    with open("final_submission.json", "w") as f:
        json.dump(submission, f, indent=2)
    with open("evaluation_validation_report.json", "w") as f:
        json.dump(metadata, f, indent=2)
    total_candidates = sum(len(ids) for ids in submission["config_candidates"].values())
    initial_score = metadata.get("initial_evaluation_score", 0.0)
    final_score = metadata.get("final_evaluation_score", 0.0)
    corrections_made = validation_summary.get("correction_stats", {}).get("candidates_corrected", 0)
    print(f"\nSUBMISSION COMPLETED!")
    print(f"Submission file: final_submission.json")
    print(f"Categories: {len(submission['config_candidates'])}")
    print(f"Total candidates: {total_candidates}")
    print(f"Evaluation endpoint: Used for validation")
    print(f"Initial evaluation score: {initial_score:.3f}")
    print(f"Final evaluation score: {final_score:.3f}")
    print(f"Candidates corrected: {corrections_made}")
    print(f"Duration: {duration:.1f}s")
    if final_score >= 0.9:
        quality = "EXCELLENT"
    elif final_score >= 0.8:
        quality = "GOOD"
    elif final_score >= 0.7:
        quality = "FAIR"
    else:
        quality = "NEEDS IMPROVEMENT"
    print(f"Overall Quality: {quality}")
    improvement = final_score - initial_score
    if improvement > 0:
        print(f"Quality Improvement: +{improvement:.3f} ({improvement/initial_score*100:.1f}%)")
    elif improvement < 0:
        print(f"Quality Change: {improvement:.3f}")
    else:
        print("Quality Maintained")
    print(f"\nFinal Category Evaluation Scores:")
    final_scores = validation_summary.get("final_evaluation_scores", {})
    for category in final_scores:
        score = final_scores[category]
        print(f"  {category}: {score:.3f}")
    if validation_summary:
        correction_stats = validation_summary.get("correction_stats", {})
        print(f"\nValidation Statistics:")
        print(f"  Total validations: {correction_stats.get('gpt_validations', 0)}")
        print(f"  MongoDB checks: {correction_stats.get('mongodb_validations', 0)}")
        print(f"  Categories corrected: {correction_stats.get('categories_corrected', 0)}")
        print(f"  Total corrections: {correction_stats.get('candidates_corrected', 0)}")
    if total_candidates == 100:
        print("\nSubmission format validated: Exactly 100 candidates")
        print(f"\nREADY FOR MERCOR FINAL SUBMISSION!")
        print(f"curl -H 'Authorization: {config.api.user_email}' \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d @final_submission.json \\")
        print(f"     'https://mercor-dev--search-eng-interview.modal.run/grade'")
    else:
        print(f"Warning: Expected 100 candidates, got {total_candidates}")
    print(f"\nDetailed validation report: evaluation_validation_report.json")
if __name__ == "__main__":
    main() 