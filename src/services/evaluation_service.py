"""Evaluation service for candidate assessment using Mercor API."""

import requests
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from ..config.settings import config
from ..models.candidate import CandidateProfile, EvaluationResult
from ..utils.logger import get_logger
from ..utils.helpers import retry_with_backoff, execute_parallel_tasks, PerformanceTimer

logger = get_logger(__name__)


class EvaluationService:
    """Service for evaluating candidate search results using Mercor API."""
    
    def __init__(self):
        self.eval_endpoint = config.api.eval_endpoint
        self.user_email = config.api.user_email
        
        if not self.user_email:
            raise ValueError("USER_EMAIL not found in environment variables")
        
        logger.info(f"Initialized EvaluationService with email: {self.user_email}")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0, backoff_factor=2.0)
    def evaluate_candidates(
        self, 
        config_name: str, 
        candidate_ids: List[str]
    ) -> Optional[EvaluationResult]:
        """
        Evaluate a list of candidates for a specific job configuration.
        
        Args:
            config_name: Name of the job configuration (e.g., "tax_lawyer.yml")
            candidate_ids: List of candidate IDs to evaluate
            
        Returns:
            EvaluationResult object or None if evaluation fails
            
        Raises:
            requests.RequestException: If API request fails
        """
        if not candidate_ids:
            logger.warning(f"No candidates provided for evaluation of {config_name}")
            return None
        
        logger.debug(f"Evaluating {len(candidate_ids)} candidates for {config_name}")
        
        headers = {
            "Authorization": self.user_email,
            "Content-Type": "application/json"
        }
        
        payload = {
            "config_path": config_name,
            "object_ids": candidate_ids[:10]  # API accepts max 10 candidates
        }
        
        try:
            with PerformanceTimer(f"API evaluation for {config_name}"):
                response = requests.post(
                    self.eval_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=config.search.request_timeout
                )
                
                response.raise_for_status()
                result_data = response.json()
            
            # Parse evaluation result
            evaluation_result = EvaluationResult(
                config_name=config_name,
                num_candidates=len(candidate_ids),
                average_final_score=result_data.get("average_final_score", 0.0),
                individual_results=result_data.get("individual_results", []),
                average_soft_scores=result_data.get("average_soft_scores", []),
                average_hard_scores=result_data.get("average_hard_scores", [])
            )
            
            logger.info(f"✅ Evaluation completed for {config_name}: {evaluation_result.average_final_score:.2f}")
            return evaluation_result
            
        except requests.RequestException as e:
            logger.error(f"❌ Evaluation failed for {config_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during evaluation of {config_name}: {e}")
            return None
    
    def evaluate_multiple_configs(
        self, 
        evaluations: List[Dict[str, Any]],
        max_workers: int = None
    ) -> Dict[str, Optional[EvaluationResult]]:
        """
        Evaluate multiple job configurations in parallel.
        
        Args:
            evaluations: List of dicts with 'config_name' and 'candidate_ids'
            max_workers: Maximum number of parallel workers
            
        Returns:
            Dictionary mapping config names to evaluation results
        """
        if max_workers is None:
            max_workers = min(config.search.thread_pool_size, len(evaluations))
        
        logger.info(f"Evaluating {len(evaluations)} configurations using {max_workers} workers")
        
        # Create evaluation tasks
        tasks = [
            lambda eval_data=eval_data: self.evaluate_candidates(
                eval_data["config_name"], 
                eval_data["candidate_ids"]
            )
            for eval_data in evaluations
        ]
        
        # Execute evaluations in parallel
        results = execute_parallel_tasks(tasks, max_workers=max_workers)
        
        # Build result dictionary
        evaluation_results = {}
        for i, eval_data in enumerate(evaluations):
            config_name = eval_data["config_name"]
            evaluation_results[config_name] = results[i] if i < len(results) else None
        
        return evaluation_results
    
    def format_evaluation_summary(
        self, 
        results: Dict[str, Optional[EvaluationResult]]
    ) -> str:
        """
        Format evaluation results into a human-readable summary.
        
        Args:
            results: Dictionary of evaluation results
            
        Returns:
            Formatted summary string
        """
        if not results:
            return "No evaluation results available"
        
        lines = [
            "🏆 EVALUATION RESULTS SUMMARY",
            "=" * 60
        ]
        
        # Calculate statistics
        valid_scores = [
            result.average_final_score 
            for result in results.values() 
            if result is not None
        ]
        
        if valid_scores:
            avg_score = sum(valid_scores) / len(valid_scores)
            lines.append(f"📊 Average Score: {avg_score:.2f}")
            lines.append(f"📈 Best Score: {max(valid_scores):.2f}")
            lines.append(f"📉 Worst Score: {min(valid_scores):.2f}")
            lines.append("")
        
        # Individual results
        lines.append("📋 Individual Results:")
        lines.append("-" * 40)
        
        # Sort by score (descending)
        sorted_results = sorted(
            [(k, v) for k, v in results.items() if v is not None],
            key=lambda x: x[1].average_final_score,
            reverse=True
        )
        
        for config_name, result in sorted_results:
            emoji = self._get_score_emoji(result.average_final_score)
            lines.append(f"{emoji} {config_name:<30}: {result.average_final_score:>8.2f}")
        
        # Failed evaluations
        failed_configs = [k for k, v in results.items() if v is None]
        if failed_configs:
            lines.append("")
            lines.append("❌ Failed Evaluations:")
            for config_name in failed_configs:
                lines.append(f"   • {config_name}")
        
        return "\n".join(lines)
    
    def _get_score_emoji(self, score: float) -> str:
        """Get appropriate emoji for a score."""
        if score >= 70:
            return "🥇"
        elif score >= 50:
            return "🥈"
        elif score >= 30:
            return "🥉"
        elif score >= 10:
            return "📈"
        else:
            return "⚠️"
    
    def save_detailed_results(
        self, 
        results: Dict[str, Optional[EvaluationResult]],
        output_file: str = "results/detailed_evaluation_results.json"
    ) -> None:
        """
        Save detailed evaluation results to a JSON file.
        
        Args:
            results: Dictionary of evaluation results
            output_file: Path to output file
        """
        from ..utils.helpers import save_json_file
        
        detailed_data = {}
        
        for config_name, result in results.items():
            if result is not None:
                detailed_data[config_name] = {
                    "average_final_score": result.average_final_score,
                    "num_candidates": result.num_candidates,
                    "individual_results": result.individual_results,
                    "average_soft_scores": result.average_soft_scores,
                    "average_hard_scores": result.average_hard_scores
                }
            else:
                detailed_data[config_name] = {"error": "Evaluation failed"}
        
        save_json_file(detailed_data, output_file)
        logger.info(f"Saved detailed evaluation results to {output_file}")
    
    def compare_strategies(
        self, 
        strategy_results: Dict[str, Dict[str, Optional[EvaluationResult]]]
    ) -> str:
        """
        Compare evaluation results across different search strategies.
        
        Args:
            strategy_results: Nested dict with strategy -> config -> result
            
        Returns:
            Formatted comparison string
        """
        lines = [
            "🔄 STRATEGY COMPARISON",
            "=" * 60
        ]
        
        # Calculate average scores per strategy
        strategy_averages = {}
        for strategy, results in strategy_results.items():
            valid_scores = [
                result.average_final_score 
                for result in results.values() 
                if result is not None
            ]
            if valid_scores:
                strategy_averages[strategy] = sum(valid_scores) / len(valid_scores)
            else:
                strategy_averages[strategy] = 0.0
        
        # Sort strategies by average score
        sorted_strategies = sorted(
            strategy_averages.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        lines.append("📊 Strategy Performance:")
        for i, (strategy, avg_score) in enumerate(sorted_strategies):
            rank_emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else "📈"
            lines.append(f"{rank_emoji} {strategy:<20}: {avg_score:>8.2f}")
        
        return "\n".join(lines)


# Global evaluation service instance
evaluation_service = EvaluationService() 