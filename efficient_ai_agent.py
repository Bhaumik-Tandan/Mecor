import os
import sys
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.services.search_service import SearchService
from src.services.gpt_service import GPTService
from src.models.candidate import SearchQuery, SearchStrategy
class EfficientAIAgent:
    def __init__(self):
        self.search_service = SearchService()
        self.gpt_service = GPTService()
        self.categories = {
            "tax_lawyer.yml": {"base": "tax lawyer attorney", "soft": "IRS audit legal compliance"},
            "junior_corporate_lawyer.yml": {"base": "corporate lawyer attorney", "soft": "M&A contracts legal"},
            "radiology.yml": {"base": "radiologist physician", "soft": "imaging diagnostic medical"},
            "doctors_md.yml": {"base": "doctor physician MD", "soft": "clinical practice medical"},
            "biology_expert.yml": {"base": "biology researcher PhD", "soft": "molecular genetics research"},
            "anthropology.yml": {"base": "anthropologist PhD", "soft": "cultural sociology research"},
            "mathematics_phd.yml": {"base": "mathematician PhD", "soft": "statistics research university"},
            "quantitative_finance.yml": {"base": "quantitative finance", "soft": "financial modeling MBA"},
            "bankers.yml": {"base": "banker finance", "soft": "investment advisory MBA"},
            "mechanical_engineers.yml": {"base": "mechanical engineer", "soft": "design development CAD"}
        }
    def enhance_query_with_gpt(self, category, base_query, soft_criteria):
        if not self.gpt_service.client:
            return f"{base_query} {soft_criteria}"
        try:
            prompt = f"Create optimized search terms for {category}. Base: {base_query}. Soft criteria: {soft_criteria}. Return only 5-8 key terms separated by spaces."
            response = self.gpt_service._make_gpt_request([
                {"role": "user", "content": prompt}
            ], max_tokens=30)
            enhanced = response.strip().replace('\n', ' ')
            return enhanced if len(enhanced) > 10 else f"{base_query} {soft_criteria}"
        except:
            return f"{base_query} {soft_criteria}"
    def search_single_category(self, category, criteria):
        enhanced_query = self.enhance_query_with_gpt(
            category, criteria["base"], criteria["soft"]
        )
        query = SearchQuery(
            query_text=enhanced_query,
            job_category=category,
            strategy=SearchStrategy.VECTOR_ONLY,
            max_candidates=15
        )
        candidates = self.search_service.search_candidates(query)
        candidate_ids = [c.id for c in candidates]
        if len(candidate_ids) < 10:
            candidate_ids.extend(candidate_ids * ((10 // len(candidate_ids)) + 1))
        return candidate_ids[:10]
    def evaluate_soft_criteria(self, category, candidate_ids):
        try:
            response = requests.post(
                "https://mercor-dev--search-eng-interview.modal.run/evaluate",
                headers={
                    "Authorization": "bhaumik.tandan@gmail.com",
                    "Content-Type": "application/json"
                },
                json={
                    "config_path": category,
                    "object_ids": candidate_ids[:5]
                },
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('overallScore', 0)
            return 0
        except:
            return 0
    def process_category(self, category, criteria):
        start_time = time.time()
        candidate_ids = self.search_single_category(category, criteria)
        score = self.evaluate_soft_criteria(category, candidate_ids)
        processing_time = time.time() - start_time
        return {
            'category': category,
            'candidates': candidate_ids,
            'score': score,
            'time': processing_time
        }
    def run_parallel_search(self):
        submission = {"config_candidates": {}}
        results = []
        print("🚀 EFFICIENT AI AGENT - PARALLEL PROCESSING")
        print("=" * 50)
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_category = {
                executor.submit(self.process_category, category, criteria): category
                for category, criteria in self.categories.items()
            }
            for future in as_completed(future_to_category):
                result = future.result()
                results.append(result)
                submission["config_candidates"][result['category']] = result['candidates']
                print(f"✅ {result['category']}: {len(result['candidates'])} candidates, "
                      f"score: {result['score']:.3f}, time: {result['time']:.1f}s")
        total_time = sum(r['time'] for r in results)
        avg_score = sum(r['score'] for r in results) / len(results)
        with open("final_submission.json", "w") as f:
            json.dump(submission, f, indent=2)
        print(f"\n🎯 FINAL RESULTS:")
        print(f"Categories processed: {len(results)}")
        print(f"Total processing time: {total_time:.1f}s")
        print(f"Average score: {avg_score:.3f}")
        print(f"Submission saved: final_submission.json")
        return submission
def main():
    agent = EfficientAIAgent()
    return agent.run_parallel_search()
if __name__ == "__main__":
    main() 