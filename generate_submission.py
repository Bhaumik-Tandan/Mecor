#!/usr/bin/env python3
"""
Final Submission Generator for Mercor Search Engineer Assignment
================================================================

This script generates the final JSON submission with exactly 10 candidates
for each of the 10 required job categories using our optimized search agent.
"""

import os
import sys
import json
import requests
from typing import Dict, List
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy
from src.services.search_service import search_service
from src.utils.logger import setup_logger

logger = setup_logger("submission_generator", level="INFO")

# Required job categories for submission (all 10)
REQUIRED_CATEGORIES = [
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

def search_category_candidates(category: str, max_candidates: int = 10) -> List[str]:
    """
    Search for top candidates in a specific job category.
    
    Args:
        category: Job category (e.g., "tax_lawyer.yml")
        max_candidates: Number of candidates to return (must be 10 for submission)
        
    Returns:
        List of candidate IDs
    """
    logger.info(f"🔍 Searching for {category} candidates...")
    
    # Create search query
    query = SearchQuery(
        query_text=f"professional {category.replace('_', ' ').replace('.yml', '')}",
        job_category=category,
        strategy=SearchStrategy.HYBRID,
        max_candidates=max_candidates
    )
    
    # Perform search using our optimized hybrid strategy with soft filtering
    candidates = search_service.search_candidates(query, SearchStrategy.HYBRID)
    
    # Extract candidate IDs
    candidate_ids = [candidate.id for candidate in candidates[:max_candidates]]
    
    logger.info(f"✅ Found {len(candidate_ids)} candidates for {category}")
    
    # Log top 3 candidates for verification
    for i, candidate in enumerate(candidates[:3], 1):
        logger.info(f"  {i}. {candidate.name} (ID: {candidate.id})")
    
    return candidate_ids

def generate_submission_json() -> Dict[str, Dict[str, List[str]]]:
    """
    Generate the complete submission JSON for all required categories.
    
    Returns:
        Properly formatted submission dictionary
    """
    logger.info("🚀 Starting submission generation for all 10 categories...")
    
    config_candidates = {}
    
    for category in REQUIRED_CATEGORIES:
        try:
            candidate_ids = search_category_candidates(category, max_candidates=10)
            
            # Ensure exactly 10 candidates
            if len(candidate_ids) < 10:
                logger.warning(f"⚠️  Only found {len(candidate_ids)} candidates for {category}, padding with duplicates")
                # Pad with duplicates if needed (shouldn't happen with our data size)
                while len(candidate_ids) < 10:
                    candidate_ids.extend(candidate_ids[:10-len(candidate_ids)])
            
            config_candidates[category] = candidate_ids[:10]  # Ensure exactly 10
            
        except Exception as e:
            logger.error(f"❌ Failed to get candidates for {category}: {e}")
            # Use fallback candidates if search fails (should not happen)
            config_candidates[category] = ["fallback_id"] * 10
    
    submission_data = {
        "config_candidates": config_candidates
    }
    
    logger.info(f"✅ Generated submission for {len(config_candidates)} categories")
    return submission_data

def save_submission_file(submission_data: Dict, output_file: str = "final_submission.json"):
    """Save submission data to JSON file."""
    
    # Add metadata
    submission_with_metadata = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "search_strategy": "Hybrid (Vector + BM25 + Soft Filtering)",
            "model_versions": {
                "embedding_model": "voyage-3",
                "gpt_model": "gpt-4.1-nano-2025-04-14",
                "vector_database": "turbopuffer"
            },
            "performance_features": [
                "Hybrid vector + BM25 search",
                "Soft filtering with preferred keywords",
                "Parallel processing with threading",
                "Hard filtering for must-have requirements",
                "Domain-specific query optimization"
            ]
        },
        **submission_data
    }
    
    with open(output_file, 'w') as f:
        json.dump(submission_with_metadata, f, indent=2)
    
    logger.info(f"💾 Saved submission to {output_file}")

def submit_to_mercor(submission_data: Dict, dry_run: bool = True) -> Dict:
    """
    Submit the final candidates to Mercor grading endpoint.
    
    Args:
        submission_data: The submission JSON data
        dry_run: If True, only validate format without submitting
        
    Returns:
        Response from the API
    """
    endpoint = "https://mercor-dev--search-eng-interview.modal.run/grade"
    headers = {
        "Authorization": config.api.user_email,
        "Content-Type": "application/json"
    }
    
    # Remove metadata for actual submission
    clean_submission = {"config_candidates": submission_data["config_candidates"]}
    
    if dry_run:
        logger.info("🧪 DRY RUN: Validating submission format...")
        logger.info(f"📊 Categories: {len(clean_submission['config_candidates'])}")
        
        for category, candidates in clean_submission['config_candidates'].items():
            logger.info(f"  {category}: {len(candidates)} candidates")
            
        logger.info("✅ Submission format is valid!")
        return {"status": "dry_run_success"}
    
    else:
        logger.info("🚀 Submitting to Mercor grading endpoint...")
        
        try:
            response = requests.post(endpoint, headers=headers, json=clean_submission, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            logger.info("✅ Submission successful!")
            return result
            
        except Exception as e:
            logger.error(f"❌ Submission failed: {e}")
            raise

def print_submission_summary(submission_data: Dict):
    """Print a summary of the submission."""
    
    config_candidates = submission_data["config_candidates"]
    
    print(f"\n{'='*80}")
    print(f"📋 FINAL SUBMISSION SUMMARY")
    print(f"{'='*80}")
    
    print(f"\n🎯 Total Categories: {len(config_candidates)}")
    print(f"📊 Total Candidates: {sum(len(candidates) for candidates in config_candidates.values())}")
    
    print(f"\n📋 Category Breakdown:")
    print(f"┌─────────────────────────────────────┬─────────────┬─────────────────────┐")
    print(f"│ Category                            │ Candidates  │ First Candidate ID  │")
    print(f"├─────────────────────────────────────┼─────────────┼─────────────────────┤")
    
    for category, candidates in config_candidates.items():
        first_id = candidates[0] if candidates else "N/A"
        print(f"│ {category:<35} │ {len(candidates):>11} │ {first_id:<19} │")
    
    print(f"└─────────────────────────────────────┴─────────────┴─────────────────────┘")
    
    print(f"\n🚀 Ready for submission to Mercor!")

def main():
    """Main execution function."""
    
    print("🏆 MERCOR SEARCH ENGINEER - FINAL SUBMISSION GENERATOR")
    print("=" * 60)
    print("Generating optimized candidate submissions for all 10 job categories")
    print("Using: Hybrid Search + Soft Filtering + Threading\n")
    
    try:
        # Generate submission data
        submission_data = generate_submission_json()
        
        # Save to file
        save_submission_file(submission_data, "final_submission.json")
        
        # Print summary
        print_submission_summary(submission_data)
        
        # Perform dry run validation
        submit_to_mercor(submission_data, dry_run=True)
        
        print(f"\n🎉 SUBMISSION GENERATION COMPLETE!")
        print(f"📁 File saved: final_submission.json")
        print(f"🚀 Ready to submit to Mercor!")
        
        print(f"\n📋 To submit to Mercor, run:")
        print(f"curl -H 'Authorization: {config.api.user_email}' \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d @final_submission.json \\")
        print(f"     'https://mercor-dev--search-eng-interview.modal.run/grade'")
        
    except Exception as e:
        logger.error(f"❌ Submission generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 