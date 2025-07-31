"""Main application entry point for the Search Agent."""
import sys
from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy
from src.services.search_service import search_service
from src.services.evaluation_service import evaluation_service
from src.utils.logger import get_logger, setup_logger
from src.utils.helpers import PerformanceTimer, save_results_to_csv

logger = setup_logger(
    name="search_agent_main",
    level="INFO",
    log_file="logs/search_agent_main.log"
)

class SearchAgent:
    """Main search agent application."""
    
    def __init__(self):
        self.search_service = search_service
        self.evaluation_service = evaluation_service
        logger.info("🚀 Initialized Search Agent")
        logger.info(f"📧 User Email: {config.api.user_email}")
        logger.info(f"🔍 Using Optimized Elite Institution Search")

    def run_evaluation(self) -> dict:
        """
        Run complete evaluation across all job categories using optimized settings.
        Returns:
            Dictionary with evaluation results and metadata
        """
        logger.info("🏆 Starting comprehensive evaluation")
        logger.info(f"📋 Categories: {len(config.job_categories)}")
        
        with PerformanceTimer("Complete evaluation"):
            logger.info("🔍 Phase 1: Searching candidates")
            search_results = {}
            
            # Search each category with simple strategy
            for category in config.job_categories:
                logger.info(f"🔍 Searching for: {category}")
                
                query = SearchQuery(
                    query_text=category.replace("_", " ").replace(".yml", ""),
                    job_category=category,
                    strategy=SearchStrategy.HYBRID,
                    max_candidates=config.search.max_candidates_per_query
                )
                
                candidates = self.search_service.search_candidates(query, SearchStrategy.HYBRID)
                search_results[category] = candidates
                logger.info(f"✅ Found {len(candidates)} candidates for {category}")

            logger.info("📊 Phase 2: Preparing evaluations")
            evaluations = []
            for category, candidates in search_results.items():
                if candidates:
                    candidate_ids = [c.id for c in candidates[:10]]  # Top 10 for evaluation
                    evaluations.append({
                        "config_name": category,
                        "candidate_ids": candidate_ids
                    })

            logger.info("🎯 Phase 3: Running evaluations")
            evaluation_results = self.evaluation_service.evaluate_multiple_configs(evaluations)

            logger.info("📈 Phase 4: Compiling results")
            final_results = {
                "strategy": "simple_hybrid_search",
                "total_categories": len(config.job_categories),
                "successful_searches": len(search_results),
                "successful_evaluations": len([r for r in evaluation_results.values() if r]),
                "evaluation_results": evaluation_results,
                "search_metadata": {
                    category: {
                        "num_candidates": len(candidates),
                        "top_candidate_ids": [c.id for c in candidates[:5]]
                    }
                    for category, candidates in search_results.items()
                }
            }

            # Calculate summary statistics
            valid_scores = [
                result.average_final_score 
                for result in evaluation_results.values() 
                if result is not None
            ]
            
            if valid_scores:
                final_results["summary_stats"] = {
                    "average_score": sum(valid_scores) / len(valid_scores),
                    "best_score": max(valid_scores),
                    "worst_score": min(valid_scores),
                    "num_scores": len(valid_scores)
                }

            logger.info("✅ Evaluation completed successfully")
            return final_results

    def save_results(self, results: dict, output_dir: str = "results") -> None:
        """Save evaluation results to files."""
        from pathlib import Path
        import dataclasses
        from .utils.helpers import save_json_file
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save detailed JSON results
        serializable_results = dict(results)
        if "evaluation_results" in serializable_results:
            eval_results = {}
            for k, v in serializable_results["evaluation_results"].items():
                if v is not None:
                    eval_results[k] = dataclasses.asdict(v)
                else:
                    eval_results[k] = None
            serializable_results["evaluation_results"] = eval_results
        
        save_json_file(serializable_results, f"{output_dir}/detailed_results.json")
        
        # Save CSV summary
        if "evaluation_results" in results:
            csv_data = []
            for config_name, eval_result in results["evaluation_results"].items():
                if eval_result:
                    csv_data.append({
                        "config_name": config_name,
                        "average_final_score": eval_result.average_final_score,
                        "num_candidates": eval_result.num_candidates,
                        "strategy": "optimized_elite_search"
                    })
            
            if csv_data:
                save_results_to_csv(csv_data, f"{output_dir}/evaluation_results.csv")
        
        logger.info(f"💾 Results saved to {output_dir}/")

def main():
    """Main entry point - simplified to run one optimized evaluation."""
    try:
        print("🚀 Starting Mercor Search Agent - Clean Submission")
        print("=" * 60)
        
        agent = SearchAgent()
        results = agent.run_evaluation()
        
        # Display results
        summary = evaluation_service.format_evaluation_summary(results["evaluation_results"])
        print(summary)
        
        # Save results
        agent.save_results(results)
        
        print("\n" + "=" * 60)
        print("🎉 Evaluation completed successfully!")
        print("📁 Results saved to results/ directory")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Application interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Application failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 