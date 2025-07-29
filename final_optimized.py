import os
import sys
import json
import requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy
def search_category(category, query_text, max_candidates=10):
    search_service = SearchService()
    query = SearchQuery(
        query_text=query_text,
        job_category=category,
        strategy=SearchStrategy.VECTOR_ONLY,
        max_candidates=max_candidates
    )
    candidates = search_service.search_candidates(query)
    return [c.id for c in candidates]
def evaluate_candidates(category, candidate_ids):
    try:
        response = requests.post(
            "https://mercor-dev--search-eng-interview.modal.run/evaluate",
            headers={
                "Authorization": "bhaumik.tandan@gmail.com",
                "Content-Type": "application/json"
            },
            json={
                "config_path": category,
                "object_ids": candidate_ids[:10]
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('overallScore', 0)
        return 0
    except:
        return 0
def main():
    categories = {
        "tax_lawyer.yml": "JD attorney tax lawyer legal IRS audit",
        "junior_corporate_lawyer.yml": "JD attorney corporate lawyer M&A legal",
        "radiology.yml": "MD doctor physician radiology radiologist imaging",
        "doctors_md.yml": "MD doctor physician medical practice clinical",
        "biology_expert.yml": "PhD biology research molecular genetics university",
        "anthropology.yml": "PhD anthropology sociology research cultural",
        "mathematics_phd.yml": "PhD mathematics statistics research university",
        "quantitative_finance.yml": "MBA finance quantitative financial modeling",
        "bankers.yml": "MBA banking investment finance advisory",
        "mechanical_engineers.yml": "engineering mechanical design development CAD"
    }
    submission = {"config_candidates": {}}
    total_score = 0
    for category, query in categories.items():
        candidate_ids = search_category(category, query)
        if len(candidate_ids) < 10:
            candidate_ids.extend(candidate_ids * ((10 // len(candidate_ids)) + 1))
        submission["config_candidates"][category] = candidate_ids[:10]
        score = evaluate_candidates(category, candidate_ids)
        total_score += score
        print(f"{category}: {len(candidate_ids)} candidates, score: {score:.3f}")
    with open("final_submission.json", "w") as f:
        json.dump(submission, f, indent=2)
    avg_score = total_score / len(categories)
    print(f"\nFinal submission created: {len(categories)} categories, avg score: {avg_score:.3f}")
    return submission
if __name__ == "__main__":
    main() 