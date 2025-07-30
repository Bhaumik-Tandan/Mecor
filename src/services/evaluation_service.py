"""Evaluation service for candidate assessment using Mercor API."""
import requests
import time
import threading
import psutil
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..config.settings import config
from ..models.candidate import CandidateProfile, EvaluationResult
from ..utils.logger import get_logger
from ..utils.helpers import retry_with_backoff, execute_parallel_tasks, PerformanceTimer

logger = get_logger(__name__)

class SafeEvaluationService:
    """Service for evaluating candidate search results with safety controls."""
    
    def __init__(self, max_workers: int = 4):
        self.eval_endpoint = config.api.eval_endpoint
        self.user_email = config.api.user_email
        self.max_workers = min(max_workers, 6)  # Hard limit to prevent overload
        self.request_session = self._create_session()
        
        if not self.user_email:
            raise ValueError("USER_EMAIL not found in environment variables")
        
        logger.info(f"Initialized SafeEvaluationService with email: {self.user_email}")
        logger.info(f"🛡️ Safety limits: max_workers={self.max_workers}, connection pooling enabled")
    
    def _create_session(self) -> requests.Session:
        """Create a session with connection pooling and retry strategy."""
        session = requests.Session()
        
        # Conservative retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            respect_retry_after_header=True
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.max_workers,
            pool_maxsize=self.max_workers * 2
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _check_system_resources(self) -> bool:
        """Check if system has enough resources to continue safely."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            # Conservative thresholds
            if cpu_percent > 80:
                logger.warning(f"⚠️ High CPU usage: {cpu_percent}% - throttling")
                time.sleep(1)
                return False
            
            if memory_percent > 85:
                logger.warning(f"⚠️ High memory usage: {memory_percent}% - throttling")
                time.sleep(1)
                return False
                
            return True
        except Exception as e:
            logger.warning(f"Could not check system resources: {e}")
            return True  # Allow operation if monitoring fails

    @retry_with_backoff(max_retries=3, base_delay=1.0, backoff_factor=2.0)
    def evaluate_candidates_safe(
        self, 
        config_name: str, 
        candidate_ids: List[str]
    ) -> Optional[EvaluationResult]:
        """
        Safely evaluate candidates with resource monitoring.
        
        Args:
            config_name: Name of the job configuration (e.g., "tax_lawyer.yml")
            candidate_ids: List of candidate IDs to evaluate
        
        Returns:
            EvaluationResult object or None if evaluation fails
        """
        if not candidate_ids:
            logger.warning(f"⚠️ No candidates provided for evaluation of {config_name}")
            return None
        
        thread_id = threading.get_ident()
        eval_start = time.time()
        
        # Check system resources before making API call
        if not self._check_system_resources():
            logger.warning(f"🧵 Thread {thread_id}: Delaying evaluation due to resource constraints")
            time.sleep(2)
        
        logger.debug(f"🧵 Thread {thread_id}: Safely evaluating {len(candidate_ids)} candidates for {config_name}")
        
        headers = {
            "Authorization": self.user_email,
            "Content-Type": "application/json"
        }
        
        payload = {
            "config_path": config_name,
            "object_ids": candidate_ids[:5]  # API accepts max 5 candidates for safety
        }
        
        try:
            with PerformanceTimer(f"Safe API evaluation for {config_name}"):
                response = self.request_session.post(
                    self.eval_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=60  # Increased timeout for safety
                )
                
                response.raise_for_status()
                result_data = response.json()
            
            evaluation_result = EvaluationResult(
                config_name=config_name,
                num_candidates=len(candidate_ids),
                average_final_score=result_data.get("average_final_score", 0.0),
                individual_results=result_data.get("individual_results", []),
                average_soft_scores=result_data.get("average_soft_scores", []),
                average_hard_scores=result_data.get("average_hard_scores", [])
            )
            
            eval_time = time.time() - eval_start
            logger.info(f"✅ Thread {thread_id}: Safe evaluation completed for {config_name}: {evaluation_result.average_final_score:.2f} (took {eval_time:.2f}s)")
            
            return evaluation_result
            
        except requests.RequestException as e:
            eval_time = time.time() - eval_start
            logger.error(f"❌ Thread {thread_id}: Safe evaluation failed for {config_name} after {eval_time:.2f}s: {e}")
            raise
        except Exception as e:
            eval_time = time.time() - eval_start
            logger.error(f"❌ Thread {thread_id}: Unexpected error during safe evaluation of {config_name} after {eval_time:.2f}s: {e}")
            return None

    def evaluate_multiple_configs_safe(
        self, 
        evaluations: List[Dict[str, Any]],
        max_workers: int = None
    ) -> Dict[str, Optional[EvaluationResult]]:
        """
        Safely evaluate multiple job configurations with resource monitoring.
        
        Args:
            evaluations: List of dicts with 'config_name' and 'candidate_ids'
            max_workers: Maximum number of parallel workers (capped for safety)
        
        Returns:
            Dictionary mapping config names to evaluation results
        """
        if max_workers is None:
            max_workers = self.max_workers
        else:
            max_workers = min(max_workers, self.max_workers)  # Safety cap
        
        logger.info(f"🛡️ Safely evaluating {len(evaluations)} configurations using {max_workers} workers")
        
        def safe_evaluate_wrapper(eval_data: Dict[str, Any]) -> Optional[EvaluationResult]:
            """Wrapper with additional safety checks."""
            try:
                # Small delay between evaluations to prevent overwhelming the API
                time.sleep(0.5)
                return self.evaluate_candidates_safe(
                eval_data["config_name"], 
                eval_data["candidate_ids"]
            )
            except Exception as e:
                logger.error(f"Safe evaluation wrapper failed for {eval_data['config_name']}: {e}")
                return None
        
        evaluation_results = {}
        completed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_config = {
                executor.submit(safe_evaluate_wrapper, eval_data): eval_data["config_name"]
                for eval_data in evaluations
            }
            
            for future in as_completed(future_to_config):
                completed += 1
                config_name = future_to_config[future]
                
                try:
                    result = future.result(timeout=120)  # 2 minute timeout per evaluation
                    evaluation_results[config_name] = result
                    
                    progress = (completed / len(evaluations)) * 100
                    logger.info(f"📊 Safe evaluation progress: {completed}/{len(evaluations)} ({progress:.1f}%)")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to get safe evaluation result for {config_name}: {e}")
                    evaluation_results[config_name] = None
        
        return evaluation_results

    # Legacy method for compatibility
    def evaluate_candidates(self, config_name: str, candidate_ids: List[str]) -> Optional[EvaluationResult]:
        """Legacy method - delegates to safe implementation."""
        return self.evaluate_candidates_safe(config_name, candidate_ids)
    
    def evaluate_multiple_configs(self, evaluations: List[Dict[str, Any]], max_workers: int = None) -> Dict[str, Optional[EvaluationResult]]:
        """Legacy method - delegates to safe implementation."""
        return self.evaluate_multiple_configs_safe(evaluations, max_workers)

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
        
        lines.append("📋 Individual Results:")
        lines.append("-" * 40)
        
        sorted_results = sorted(
            [(k, v) for k, v in results.items() if v is not None],
            key=lambda x: x[1].average_final_score,
            reverse=True
        )
        
        for config_name, result in sorted_results:
            emoji = self._get_score_emoji(result.average_final_score)
            lines.append(f"{emoji} {config_name:<30}: {result.average_final_score:>8.2f}")
        
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
        logger.info(f"💾 Saved detailed evaluation results to {output_file}")

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

class EvaluationService(SafeEvaluationService):
    """Main evaluation service - inherits safe implementation."""
    pass

evaluation_service = EvaluationService(max_workers=4)  # Conservative default 