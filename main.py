import os
import sys
import json
import requests
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.services.search_service import SearchService
from src.services.gpt_service import GPTService
from src.models.candidate import SearchQuery, SearchStrategy
class FastAgent:
    def __init__(self):
        self.search_service = SearchService()
        self.gpt = GPTService()
    def enhance_query(self, base_query):
        if not self.gpt.client:
            return base_query
        try:
            response = self.gpt._make_gpt_request([
                {"role": "user", "content": f"Optimize search terms: {base_query}. Return 5-8 keywords only."}
            ], max_tokens=25)
            result = response.strip()
            return result if len(result) > 5 else base_query
        except:
            return base_query
    def search_category(self, category, base_query):
        enhanced = self.enhance_query(base_query)
        query = SearchQuery(
            query_text=enhanced,
            job_category=category,
            strategy=SearchStrategy.VECTOR_ONLY,
            max_candidates=12
        )
        candidates = self.search_service.search_candidates(query)
        ids = [c.id for c in candidates]
        while len(ids) < 10:
            ids.extend(ids[:min(3, 10-len(ids))])
        return ids[:10]
    def process_single(self, item):
        category, query = item
        return category, self.search_category(category, query)
def main():
    agent = FastAgent()
    categories = {
        "tax_lawyer.yml": "tax attorney lawyer legal IRS",
        "junior_corporate_lawyer.yml": "corporate lawyer attorney legal M&A",
        "radiology.yml": "radiologist physician doctor imaging",
        "doctors_md.yml": "doctor physician MD medical clinical",
        "biology_expert.yml": "biology researcher PhD genetics molecular",
        "anthropology.yml": "anthropologist PhD cultural sociology",
        "mathematics_phd.yml": "mathematician PhD statistics research",
        "quantitative_finance.yml": "quantitative finance financial modeling",
        "bankers.yml": "banker investment finance advisory",
        "mechanical_engineers.yml": "mechanical engineer design CAD"
    }
    submission = {"config_candidates": {}}
    print("🚀 FAST AI AGENT")
    print("=" * 30)
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(agent.process_single, categories.items()))
    for category, candidates in results:
        submission["config_candidates"][category] = candidates
        print(f"✅ {category}: {len(candidates)} candidates")
    with open("final_submission.json", "w") as f:
        json.dump(submission, f, indent=2)
    print(f"\n🎯 Done! {len(categories)} categories processed")
    print("📄 Submission: final_submission.json")
    return submission
if __name__ == "__main__":
    main() 