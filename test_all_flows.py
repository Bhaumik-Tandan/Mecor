import os
import sys
import time
import json
import requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.services.search_service import SearchService
from src.services.gpt_service import GPTService
from src.models.candidate import SearchQuery, SearchStrategy
def test_simple_submission():
    start = time.time()
    search_service = SearchService()
    query = SearchQuery(
        query_text="PhD biology research molecular genetics university",
        job_category="biology_expert.yml",
        strategy=SearchStrategy.VECTOR_ONLY,
        max_candidates=10
    )
    candidates = search_service.search_candidates(query)
    candidate_ids = [c.id for c in candidates]
    end = time.time()
    return {
        'method': 'Simple Submission',
        'time': end - start,
        'candidates': len(candidate_ids),
        'ids': candidate_ids,
        'efficiency': len(candidate_ids) / (end - start)
    }
def test_gpt_enhanced():
    start = time.time()
    search_service = SearchService()
    gpt_service = GPTService()
    enhanced_query = "PhD biology research"
    if gpt_service.client:
        try:
            enhanced_query = gpt_service._make_gpt_request([
                {"role": "user", "content": "Create search query for PhD biology researchers. Return only terms."}
            ], max_tokens=20).strip()
        except:
            pass
    query = SearchQuery(
        query_text=enhanced_query,
        job_category="biology_expert.yml", 
        strategy=SearchStrategy.HYBRID,
        max_candidates=10
    )
    candidates = search_service.search_candidates(query)
    candidate_ids = [c.id for c in candidates]
    end = time.time()
    return {
        'method': 'GPT Enhanced',
        'time': end - start,
        'candidates': len(candidate_ids),
        'ids': candidate_ids,
        'efficiency': len(candidate_ids) / (end - start)
    }
def test_submission_agent():
    start = time.time()
    try:
        from submission_agent import SubmissionAgent
        agent = SubmissionAgent()
        candidates = agent.search_with_criteria("biology_expert.yml", max_candidates=10)
        candidate_ids = [c.id if hasattr(c, 'id') else c for c in candidates]
    except Exception as e:
        print(f"Submission agent failed: {e}")
        candidate_ids = []
    end = time.time()
    return {
        'method': 'Submission Agent',
        'time': end - start,
        'candidates': len(candidate_ids),
        'ids': candidate_ids,
        'efficiency': len(candidate_ids) / (end - start) if (end - start) > 0 else 0
    }
def test_evaluation_api(candidate_ids):
    if not candidate_ids:
        return {'success': False, 'error': 'No candidates'}
    try:
        response = requests.post(
            "https://mercor-dev--search-eng-interview.modal.run/evaluate",
            headers={
                "Authorization": "bhaumik.tandan@gmail.com",
                "Content-Type": "application/json"
            },
            json={
                "config": "biology_expert.yml",
                "candidate_ids": candidate_ids[:5]
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'score': data.get('overallScore', 0),
                'details': data
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}
def main():
    print("🔧 TESTING ALL FLOWS FOR BIOLOGY_EXPERT")
    print("=" * 50)
    flows = [
        test_simple_submission(),
        test_gpt_enhanced(), 
        test_submission_agent()
    ]
    print("\n📊 FLOW COMPARISON:")
    for flow in flows:
        print(f"{flow['method']}: {flow['efficiency']:.2f} candidates/sec ({flow['candidates']} in {flow['time']:.2f}s)")
    best_flow = max(flows, key=lambda x: x['efficiency'])
    print(f"\n🏆 MOST EFFICIENT: {best_flow['method']}")
    print("\n📡 TESTING EVALUATION API:")
    eval_result = test_evaluation_api(best_flow['ids'])
    if eval_result['success']:
        print(f"✅ Evaluation Score: {eval_result['score']}")
    else:
        print(f"❌ Evaluation Failed: {eval_result['error']}")
    result = {
        'flows': flows,
        'best_flow': best_flow['method'],
        'evaluation': eval_result
    }
    with open("flow_test_results.json", "w") as f:
        json.dump(result, f, indent=2)
    return best_flow['method']
if __name__ == "__main__":
    main() 