"""Main application entry point for the Search Agent."""

import argparse
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

from .config.settings import config
from .models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from .services.search_service import search_service
from .services.evaluation_service import evaluation_service
from .services.gpt_service import gpt_service
from .utils.logger import get_logger, setup_logger
from .utils.helpers import (
    PerformanceTimer, save_results_to_csv, format_performance_metrics,
    execute_parallel_tasks
)

# Setup logging
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
        self.gpt_service = gpt_service
        
        logger.info("🚀 Initialized Search Agent")
        logger.info(f"📧 User Email: {config.api.user_email}")
        logger.info(f"🔍 Search Strategy: Hybrid (Vector + BM25)")
        logger.info(f"🧠 GPT Enhancement: {'Enabled' if gpt_service.is_available() else 'Disabled'}")
    
    def search_single_category(
        self, 
        job_category: str, 
        strategy: SearchStrategy = SearchStrategy.HYBRID,
        max_candidates: int = 100,
        use_gpt_enhancement: bool = False
    ) -> List[CandidateProfile]:
        """
        Search for candidates in a single job category.
        
        Args:
            job_category: Job category to search (e.g., "tax_lawyer.yml")
            strategy: Search strategy to use
            max_candidates: Maximum number of candidates to return
            use_gpt_enhancement: Whether to use GPT for query enhancement
            
        Returns:
            List of candidate profiles
        """
        logger.info(f"🔍 Starting search for category: {job_category}")
        
        with PerformanceTimer(f"Search for {job_category}"):
            # Generate search query
            base_query = job_category.replace("_", " ").replace(".yml", "")
            
            if use_gpt_enhancement and self.gpt_service.is_available():
                logger.info("🧠 Using GPT query enhancement")
                enhanced_queries = self.gpt_service.enhance_query(job_category)
                query_text = enhanced_queries[0] if enhanced_queries else base_query
            else:
                query_text = base_query
            
            # Create search query object
            search_query = SearchQuery(
                query_text=query_text,
                job_category=job_category,
                strategy=strategy,
                max_candidates=max_candidates
            )
            
            # Perform search
            candidates = self.search_service.search_candidates(search_query, strategy)
            
            # Optional GPT reranking
            if use_gpt_enhancement and self.gpt_service.is_available() and candidates:
                logger.info("🧠 Using GPT candidate reranking")
                candidates = self.gpt_service.rerank_candidates(
                    job_category, candidates, top_k=max_candidates
                )
            
            logger.info(f"✅ Found {len(candidates)} candidates for {job_category}")
            return candidates
    
    def run_full_evaluation(
        self, 
        strategy: SearchStrategy = SearchStrategy.HYBRID,
        use_gpt_enhancement: bool = False,
        max_workers: int = None
    ) -> Dict[str, Any]:
        """
        Run full evaluation across all job categories.
        
        Args:
            strategy: Search strategy to use
            use_gpt_enhancement: Whether to use GPT enhancement
            max_workers: Maximum number of parallel workers
            
        Returns:
            Dictionary with evaluation results and metadata
        """
        logger.info("🏆 Starting full evaluation pipeline")
        logger.info(f"📋 Categories: {len(config.job_categories)}")
        logger.info(f"🔧 Strategy: {strategy.value}")
        logger.info(f"🧠 GPT Enhancement: {use_gpt_enhancement}")
        
        with PerformanceTimer("Full evaluation pipeline"):
            
            # Step 1: Search for candidates in all categories
            logger.info("🔍 Phase 1: Searching candidates")
            search_results = {}
            
            if max_workers and max_workers > 1:
                # Parallel search
                search_tasks = [
                    lambda cat=category: (
                        category, 
                        self.search_single_category(
                            category, strategy, 
                            config.search.max_candidates_per_query,
                            use_gpt_enhancement
                        )
                    )
                    for category in config.job_categories
                ]
                
                task_results = execute_parallel_tasks(search_tasks, max_workers)
                search_results = {cat: candidates for cat, candidates in task_results if candidates}
                
            else:
                # Sequential search
                for category in config.job_categories:
                    candidates = self.search_single_category(
                        category, strategy, 
                        config.search.max_candidates_per_query,
                        use_gpt_enhancement
                    )
                    search_results[category] = candidates
            
            # Step 2: Prepare evaluation data
            logger.info("📊 Phase 2: Preparing evaluations")
            evaluations = []
            for category, candidates in search_results.items():
                if candidates:
                    candidate_ids = [c.id for c in candidates[:10]]  # Top 10 for evaluation
                    evaluations.append({
                        "config_name": category,
                        "candidate_ids": candidate_ids
                    })
            
            # Step 3: Run evaluations
            logger.info("🎯 Phase 3: Running evaluations")
            evaluation_results = self.evaluation_service.evaluate_multiple_configs(
                evaluations, max_workers
            )
            
            # Step 4: Compile results
            logger.info("📈 Phase 4: Compiling results")
            final_results = {
                "strategy": strategy.value,
                "gpt_enhancement": use_gpt_enhancement,
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
            
            logger.info("✅ Full evaluation completed successfully")
            return final_results
    
    def compare_strategies(
        self, 
        strategies: List[SearchStrategy],
        use_gpt_enhancement: bool = False
    ) -> Dict[str, Any]:
        """
        Compare multiple search strategies.
        
        Args:
            strategies: List of search strategies to compare
            use_gpt_enhancement: Whether to use GPT enhancement
            
        Returns:
            Comparison results
        """
        logger.info(f"🔄 Comparing {len(strategies)} search strategies")
        
        strategy_results = {}
        
        for strategy in strategies:
            logger.info(f"🧪 Testing strategy: {strategy.value}")
            results = self.run_full_evaluation(strategy, use_gpt_enhancement)
            strategy_results[strategy.value] = results
        
        # Generate comparison summary
        comparison_summary = self.evaluation_service.compare_strategies({
            strategy: results["evaluation_results"] 
            for strategy, results in strategy_results.items()
        })
        
        return {
            "strategy_results": strategy_results,
            "comparison_summary": comparison_summary
        }
    
    def save_results(
        self, 
        results: Dict[str, Any], 
        output_dir: str = "results"
    ) -> None:
        """
        Save evaluation results to files.
        
        Args:
            results: Results dictionary to save
            output_dir: Directory to save results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save detailed JSON results (convert dataclasses to dicts)
        from .utils.helpers import save_json_file
        import dataclasses
        
        # Convert EvaluationResult objects to dictionaries
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
        
        # Save evaluation results to CSV
        if "evaluation_results" in results:
            csv_data = []
            for config_name, eval_result in results["evaluation_results"].items():
                if eval_result:
                    csv_data.append({
                        "config_name": config_name,
                        "average_final_score": eval_result.average_final_score,
                        "num_candidates": eval_result.num_candidates,
                        "strategy": results.get("strategy", "unknown"),
                        "gpt_enhancement": results.get("gpt_enhancement", False)
                    })
            
            if csv_data:
                save_results_to_csv(csv_data, f"{output_dir}/evaluation_results.csv")
        
        logger.info(f"💾 Results saved to {output_dir}/")


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Advanced Search Agent for Candidate Retrieval")
    
    parser.add_argument(
        "--strategy", 
        choices=["vector", "bm25", "hybrid", "gpt_enhanced"],
        default="hybrid",
        help="Search strategy to use"
    )
    
    parser.add_argument(
        "--category",
        type=str,
        help="Single job category to search (e.g., 'tax_lawyer.yml')"
    )
    
    parser.add_argument(
        "--gpt-enhancement",
        action="store_true",
        help="Enable GPT-based query enhancement and reranking"
    )
    
    parser.add_argument(
        "--compare-strategies",
        action="store_true",
        help="Compare multiple search strategies"
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=config.search.thread_pool_size,
        help="Maximum number of parallel workers"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Directory to save results"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging with specified level
    global logger
    logger = setup_logger(
        name="search_agent_main",
        level=args.log_level,
        log_file="logs/search_agent_main.log"
    )
    
    # Map strategy strings to enums
    strategy_map = {
        "vector": SearchStrategy.VECTOR_ONLY,
        "bm25": SearchStrategy.BM25_ONLY,
        "hybrid": SearchStrategy.HYBRID,
        "gpt_enhanced": SearchStrategy.GPT_ENHANCED
    }
    
    try:
        # Initialize search agent
        agent = SearchAgent()
        
        if args.compare_strategies:
            # Compare multiple strategies
            strategies = [SearchStrategy.VECTOR_ONLY, SearchStrategy.BM25_ONLY, SearchStrategy.HYBRID]
            if args.gpt_enhancement:
                strategies.append(SearchStrategy.GPT_ENHANCED)
            
            results = agent.compare_strategies(strategies, args.gpt_enhancement)
            print(results["comparison_summary"])
            agent.save_results(results, args.output_dir)
            
        elif args.category:
            # Search single category
            strategy = strategy_map[args.strategy]
            candidates = agent.search_single_category(
                args.category, strategy, 
                config.search.top_k_results, 
                args.gpt_enhancement
            )
            
            print(f"\n🔍 Found {len(candidates)} candidates for {args.category}:")
            for i, candidate in enumerate(candidates[:10], 1):
                print(f"{i:2d}. {candidate.name} ({candidate.id})")
                if candidate.summary:
                    print(f"    {candidate.summary[:100]}...")
                print()
            
        else:
            # Run full evaluation
            strategy = strategy_map[args.strategy]
            results = agent.run_full_evaluation(
                strategy, args.gpt_enhancement, args.max_workers
            )
            
            # Display results
            summary = evaluation_service.format_evaluation_summary(
                results["evaluation_results"]
            )
            print(summary)
            
            # Save results
            agent.save_results(results, args.output_dir)
        
        logger.info("🎉 Application completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Application interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Application failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 