"""
Enhanced Search Strategy for Low-Performing Categories
====================================================
Targeted improvements for categories failing official Mercor criteria.
"""
import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.config.settings import config
from src.models.candidate import SearchQuery, SearchStrategy
from src.services.search_service import search_service
class TargetedSearchStrategy:
    """Enhanced search for categories failing official criteria."""
    def __init__(self):
        self.search_service = search_service
        self.enhanced_queries = {
            "biology_expert.yml": [
                "PhD biology molecular genetics research university",
                "doctorate biological sciences cell biology research",
                "PhD biologist molecular biology genetics publications",
                "biology PhD researcher university laboratory",
                "biological sciences doctorate research publications"
            ],
            "tax_lawyer.yml": [
                "JD attorney tax lawyer law school IRS",
                "juris doctor tax attorney legal practice",
                "attorney JD tax law IRS audit compliance", 
                "tax lawyer JD degree law school attorney",
                "legal counsel JD tax attorney law"
            ],
            "junior_corporate_lawyer.yml": [
                "JD attorney corporate lawyer M&A law school",
                "corporate attorney JD mergers acquisitions legal",
                "attorney JD corporate law contracts legal practice",
                "legal counsel JD corporate transactions attorney",
                "corporate lawyer JD attorney due diligence"
            ],
            "doctors_md.yml": [
                "MD physician doctor medical practice clinical",
                "doctor MD general practitioner primary care",
                "physician MD clinical practice family medicine",
                "MD doctor medical practice GP healthcare",
                "medical doctor MD physician clinical care"
            ],
            "mathematics_phd.yml": [
                "PhD mathematics mathematical research university",
                "mathematics PhD researcher mathematical modeling",
                "PhD mathematician statistics research university",
                "mathematical sciences PhD research doctorate",
                "mathematics doctorate PhD research publications"
            ],
            "quantitative_finance.yml": [
                "MBA finance quantitative financial modeling",
                "quantitative finance MBA risk modeling investment",
                "financial engineering MBA quantitative analysis",
                "MBA quantitative analyst finance derivatives",
                "finance MBA quantitative trading financial"
            ]
        }
    def enhanced_search_for_category(self, category: str, max_candidates: int = 50):
        """Perform enhanced search for a specific category."""
        print(f"🎯 Enhanced search for {category}")
        if category not in self.enhanced_queries:
            print(f"No enhanced strategy for {category}")
            return []
        all_candidates = []
        queries = self.enhanced_queries[category]
        for i, query_text in enumerate(queries):
            print(f"  Query {i+1}/{len(queries)}: {query_text}")
            for strategy in [SearchStrategy.VECTOR_ONLY, SearchStrategy.HYBRID, SearchStrategy.BM25_ONLY]:
                query = SearchQuery(
                    query_text=query_text,
                    job_category=category,
                    strategy=strategy,
                    max_candidates=max_candidates // len(queries)
                )
                candidates = self.search_service.search_candidates(query, strategy)
                all_candidates.extend(candidates)
        seen_ids = set()
        unique_candidates = []
        for candidate in all_candidates:
            if candidate.id not in seen_ids:
                seen_ids.add(candidate.id)
                unique_candidates.append(candidate)
        print(f"  Found {len(unique_candidates)} unique candidates")
        return unique_candidates[:max_candidates]
    def generate_enhanced_submission(self):
        """Generate submission with enhanced search for failing categories."""
        print("🚀 GENERATING ENHANCED SUBMISSION FOR FAILING CATEGORIES")
        print("=" * 60)
        failing_categories = [
            "biology_expert.yml",
            "tax_lawyer.yml", 
            "junior_corporate_lawyer.yml",
            "doctors_md.yml",
            "mathematics_phd.yml",
            "quantitative_finance.yml"
        ]
        enhanced_submission = {}
        for category in failing_categories:
            candidates = self.enhanced_search_for_category(category, max_candidates=20)
            top_candidates = candidates[:10]
            if len(top_candidates) < 10:
                while len(top_candidates) < 10:
                    top_candidates.extend(candidates[:10-len(top_candidates)])
            enhanced_submission[category] = [c.id for c in top_candidates[:10]]
            print(f"✅ {category}: {len(enhanced_submission[category])} candidates selected")
        try:
            with open("final_submission.json", "r") as f:
                existing_submission = json.load(f)
            good_categories = ["bankers.yml", "mechanical_engineers.yml", "radiology.yml", "anthropology.yml"]
            for category in good_categories:
                if category in existing_submission["config_candidates"]:
                    enhanced_submission[category] = existing_submission["config_candidates"][category]
                    print(f"✅ {category}: Kept existing high-performing candidates")
        except Exception as e:
            print(f"Warning: Could not load existing submission: {e}")
        final_submission = {"config_candidates": enhanced_submission}
        with open("enhanced_final_submission.json", "w") as f:
            json.dump(final_submission, f, indent=2)
        print(f"\n🎉 Enhanced submission saved to: enhanced_final_submission.json")
        print(f"📊 Total categories: {len(enhanced_submission)}")
        print(f"👥 Total candidates: {sum(len(ids) for ids in enhanced_submission.values())}")
        return enhanced_submission
def main():
    """Main function to generate enhanced submission."""
    strategy = TargetedSearchStrategy()
    strategy.generate_enhanced_submission()
if __name__ == "__main__":
    main() 