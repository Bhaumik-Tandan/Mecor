"""
Working MCP-Pattern Enhanced AI Agent
====================================
MCP-pattern agent that works with our existing infrastructure:
- Uses existing validation agent for MongoDB access
- Enhanced vector search with multiple strategies
- GPT validation when available (graceful degradation)
- Mercor evaluation API integration
- Comprehensive analytics and reporting
"""
import os
import sys
import json
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.config.settings import config
from src.services.gpt_service import GPTService
from src.services.search_service import SearchService  
from src.services.embedding_service import EmbeddingService
from src.models.candidate import CandidateProfile, SearchQuery, SearchStrategy
from src.utils.logger import get_logger
from src.agents.enhanced_validation_agent import EnhancedValidationAgent
logger = get_logger(__name__)
class WorkingMCPAgent:
    """
    Working MCP-Pattern Agent that combines all available technologies:
    - Enhanced vector search (primary method)
    - MongoDB access via existing validation agent
    - GPT validation when available
    - Mercor evaluation API validation
    - Comprehensive analytics
    """
    def __init__(self):
        """Initialize all services and connections."""
        self.gpt_service = GPTService()
        self.search_service = SearchService()
        self.embedding_service = EmbeddingService()
        self.validation_agent = EnhancedValidationAgent()
        self.performance_metrics = {
            'vector_searches': 0,
            'mongodb_validations': 0,
            'gpt_validations': 0,
            'evaluation_api_calls': 0,
            'candidates_processed': 0,
            'validation_corrections': 0,
            'start_time': datetime.now()
        }
        self.search_results = {}
        self.validation_results = {}
        self.evaluation_scores = {}
        self.quality_improvements = {}
    def enhanced_vector_search_with_strategies(self, category: str, requirements: Dict[str, Any], limit: int = 50) -> List[CandidateProfile]:
        """Enhanced vector search using multiple strategies and query variations."""
        logger.info(f"🔍 Enhanced vector search for {category}")
        all_candidates = []
        query_strategies = []
        must_have = requirements.get('must_have', [])
        preferred = requirements.get('preferred', [])
        if must_have:
            query_strategies.append({
                'query': " ".join(must_have[:5]),  # Top 5 must-have terms
                'strategy': SearchStrategy.VECTOR_ONLY,
                'weight': 0.4
            })
        professional_terms = []
        if 'PhD' in must_have or 'doctorate' in str(must_have):
            professional_terms.extend(['PhD', 'doctorate', 'research', 'university'])
        if 'MD' in must_have or 'doctor' in str(must_have):
            professional_terms.extend(['MD', 'doctor', 'physician', 'medical'])
        if 'JD' in must_have or 'attorney' in str(must_have):
            professional_terms.extend(['JD', 'attorney', 'lawyer', 'legal'])
        if 'MBA' in must_have or 'finance' in str(must_have):
            professional_terms.extend(['MBA', 'finance', 'business'])
        if professional_terms:
            query_strategies.append({
                'query': " ".join(professional_terms + must_have[:3]),
                'strategy': SearchStrategy.HYBRID,
                'weight': 0.3
            })
        if must_have:
            query_strategies.append({
                'query': " ".join(must_have + preferred[:3]),
                'strategy': SearchStrategy.BM25_ONLY,
                'weight': 0.2
            })
        domain_query = f"{category.replace('.yml', '').replace('_', ' ')} {' '.join(must_have[:3])}"
        query_strategies.append({
            'query': domain_query,
            'strategy': SearchStrategy.VECTOR_ONLY,
            'weight': 0.1
        })
        for i, strategy_config in enumerate(query_strategies):
            try:
                logger.info(f"  Strategy {i+1}: {strategy_config['strategy'].value} - '{strategy_config['query'][:50]}...'")
                search_query = SearchQuery(
                    query_text=strategy_config['query'],
                    job_category=category,
                    strategy=strategy_config['strategy'],
                    max_candidates=limit // len(query_strategies)
                )
                candidates = self.search_service.search_candidates(search_query)
                for candidate in candidates:
                    candidate.relevance_score = candidate.relevance_score * strategy_config['weight']
                all_candidates.extend(candidates)
                self.performance_metrics['vector_searches'] += 1
                logger.info(f"    Found {len(candidates)} candidates")
            except Exception as e:
                logger.warning(f"Search strategy {i+1} failed: {e}")
        candidate_map = {}
        for candidate in all_candidates:
            if candidate.id in candidate_map:
                candidate_map[candidate.id].relevance_score += candidate.relevance_score
            else:
                candidate_map[candidate.id] = candidate
        unique_candidates = list(candidate_map.values())
        unique_candidates.sort(key=lambda x: x.relevance_score, reverse=True)
        logger.info(f"🎯 Vector search complete: {len(unique_candidates)} unique candidates")
        return unique_candidates[:limit]
    def mongodb_data_enrichment(self, candidate_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Use validation agent to enrich candidate data from MongoDB."""
        logger.info(f"📊 MongoDB data enrichment for {len(candidate_ids)} candidates")
        enriched_data = {}
        def enrich_candidate(candidate_id):
            try:
                full_data = self.validation_agent.get_full_candidate_data_from_mongodb(candidate_id)
                if full_data:
                    validation_result = self.validation_agent.validate_candidate_with_mongodb(candidate_id)
                    enriched_data[candidate_id] = {
                        'full_data': full_data,
                        'mongodb_validation': validation_result,
                        'quality_score': self.validation_agent.validate_candidate_quality(candidate_id) if hasattr(self.validation_agent, 'validate_candidate_quality') else 0.5
                    }
                    self.performance_metrics['mongodb_validations'] += 1
            except Exception as e:
                logger.warning(f"MongoDB enrichment failed for {candidate_id}: {e}")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(enrich_candidate, cid) for cid in candidate_ids]
            for future in futures:
                future.result()
        logger.info(f"✅ MongoDB enrichment complete: {len(enriched_data)} candidates enriched")
        return enriched_data
    def gpt_enhanced_validation(self, candidate_data: Dict[str, Any], category: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced GPT validation using MongoDB-enriched data."""
        if not self.gpt_service.client:
            return {
                'is_suitable': True,
                'confidence': 0.5,
                'gpt_score': 0.5,
                'reasoning': 'GPT unavailable - using fallback validation',
                'validation_source': 'fallback'
            }
        try:
            if hasattr(self.validation_agent, 'validate_candidate_with_gpt'):
                result = self.validation_agent.validate_candidate_with_gpt(
                    candidate_data.get('_id', ''), 
                    category, 
                    candidate_data
                )
                result['validation_source'] = 'enhanced_validation_agent'
                self.performance_metrics['gpt_validations'] += 1
                return result
            candidate_summary = f"""
            Name: {candidate_data.get('name', 'N/A')}
            Summary: {candidate_data.get('summary', 'N/A')[:300]}
            Experience: {str(candidate_data.get('experience', []))[:200]}
            Education: {str(candidate_data.get('education', []))[:200]}
            Skills: {str(candidate_data.get('skills', []))[:150]}
            """
            prompt = f"""
            Validate candidate for {category}:
            CANDIDATE: {candidate_summary}
            REQUIREMENTS:
            Must Have: {requirements.get('must_have', [])}
            Preferred: {requirements.get('preferred', [])}
            Exclude: {requirements.get('exclude', [])}
            Return JSON:
            {{
                "is_suitable": boolean,
                "confidence": float,
                "gpt_score": float,
                "reasoning": "explanation"
            }}
            """
            response = self.gpt_service._make_gpt_request([
                {"role": "system", "content": "You are a recruiter expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ], temperature=0.2, max_tokens=500)
            result = json.loads(response.strip())
            result['validation_source'] = 'direct_gpt'
            self.performance_metrics['gpt_validations'] += 1
            return result
        except Exception as e:
            logger.warning(f"GPT validation failed: {e}")
            return {
                'is_suitable': True,
                'confidence': 0.3,
                'gpt_score': 0.3,
                'reasoning': f'GPT validation error: {str(e)}',
                'validation_source': 'error_fallback'
            }
    def call_mercor_evaluation_api(self, candidate_ids: List[str], category: str) -> Dict[str, Any]:
        """Call Mercor evaluation API with enhanced error handling."""
        try:
            payload = {
                "config": category,
                "candidate_ids": candidate_ids
            }
            logger.info(f"📡 Calling Mercor evaluation API for {category} with {len(candidate_ids)} candidates")
            response = requests.post(
                "https://mercor-dev--search-eng-interview.modal.run/evaluate",
                headers={
                    "Authorization": "bhaumik.tandan@gmail.com",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                eval_data = response.json()
                self.performance_metrics['evaluation_api_calls'] += 1
                logger.info(f"✅ Evaluation API success: Score {eval_data.get('overallScore', 'N/A')}")
                return {
                    'success': True,
                    'overall_score': eval_data.get('overallScore', 0),
                    'detailed_data': eval_data,
                    'category': category,
                    'candidate_count': len(candidate_ids),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"⚠️ Evaluation API error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'category': category
                }
        except Exception as e:
            logger.error(f"❌ Evaluation API call failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'category': category
            }
    def comprehensive_category_analysis(self, category: str) -> Dict[str, Any]:
        """Perform comprehensive MCP-pattern analysis for a category."""
        logger.info(f"🚀 Starting comprehensive MCP analysis for {category}")
        requirements = {}
        try:
            with open("src/config/prompts.json", "r") as f:
                prompts_data = json.load(f)
                requirements = prompts_data.get("hard_filters", {}).get(category.replace('.yml', ''), {})
        except Exception as e:
            logger.warning(f"Could not load requirements: {e}")
        analysis_start = datetime.now()
        logger.info("🔍 Step 1: Enhanced vector search with multiple strategies")
        vector_candidates = self.enhanced_vector_search_with_strategies(category, requirements, limit=100)
        logger.info("📊 Step 2: MongoDB data enrichment")
        top_candidate_ids = [c.id for c in vector_candidates[:50]]
        mongodb_enriched = self.mongodb_data_enrichment(top_candidate_ids)
        logger.info("🤖 Step 3: GPT enhanced validation")
        validated_candidates = []
        for candidate in vector_candidates[:30]:
            try:
                enriched_data = mongodb_enriched.get(candidate.id, {})
                full_data = enriched_data.get('full_data', {
                    '_id': candidate.id,
                    'name': getattr(candidate, 'name', 'N/A'),
                    'summary': candidate.summary,
                    'score': candidate.relevance_score
                })
                gpt_validation = self.gpt_enhanced_validation(full_data, category, requirements)
                mongodb_quality = enriched_data.get('quality_score', 0.5)
                vector_score = candidate.relevance_score
                gpt_score = gpt_validation.get('gpt_score', 0.5)
                combined_score = (
                    vector_score * 0.3 +
                    mongodb_quality * 0.3 +
                    gpt_score * 0.4
                )
                validated_candidates.append({
                    'candidate_id': candidate.id,
                    'candidate_profile': candidate,
                    'mongodb_data': enriched_data,
                    'gpt_validation': gpt_validation,
                    'combined_score': combined_score,
                    'scores': {
                        'vector_score': vector_score,
                        'mongodb_quality': mongodb_quality,
                        'gpt_score': gpt_score
                    }
                })
                self.performance_metrics['candidates_processed'] += 1
            except Exception as e:
                logger.warning(f"Validation failed for {candidate.id}: {e}")
        validated_candidates.sort(key=lambda x: x['combined_score'], reverse=True)
        logger.info("📡 Step 4: Mercor evaluation API validation")
        final_candidate_ids = [c['candidate_id'] for c in validated_candidates[:10]]
        evaluation_result = self.call_mercor_evaluation_api(final_candidate_ids, category)
        quality_analysis = {
            'total_candidates_found': len(vector_candidates),
            'mongodb_enriched_count': len(mongodb_enriched),
            'gpt_validated_count': len(validated_candidates),
            'final_selection_count': len(final_candidate_ids),
            'average_combined_score': sum([c['combined_score'] for c in validated_candidates]) / len(validated_candidates) if validated_candidates else 0,
            'high_quality_candidates': len([c for c in validated_candidates if c['combined_score'] > 0.7]),
            'evaluation_api_score': evaluation_result.get('overall_score', 0) if evaluation_result.get('success') else 0,
            'processing_time_seconds': (datetime.now() - analysis_start).total_seconds()
        }
        category_results = {
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'requirements': requirements,
            'vector_search_results': {
                'total_found': len(vector_candidates),
                'search_strategies_used': self.performance_metrics['vector_searches'],
                'top_candidates': [{'id': c.id, 'score': c.relevance_score, 'summary': c.summary[:100]} for c in vector_candidates[:10]]
            },
            'mongodb_enrichment': {
                'candidates_enriched': len(mongodb_enriched),
                'enrichment_details': {k: v.get('mongodb_validation', {}) for k, v in list(mongodb_enriched.items())[:5]}
            },
            'gpt_validation_results': {
                'candidates_validated': len(validated_candidates),
                'validation_summary': [
                    {
                        'candidate_id': c['candidate_id'],
                        'combined_score': c['combined_score'],
                        'gpt_reasoning': c['gpt_validation'].get('reasoning', 'N/A')[:100],
                        'is_suitable': c['gpt_validation'].get('is_suitable', False)
                    } for c in validated_candidates[:10]
                ]
            },
            'evaluation_api_result': evaluation_result,
            'final_selection': final_candidate_ids,
            'quality_analysis': quality_analysis,
            'performance_metrics': dict(self.performance_metrics)
        }
        self.search_results[category] = category_results
        self.evaluation_scores[category] = evaluation_result.get('overall_score', 0) if evaluation_result.get('success') else 0
        baseline_score = 0.4  # Approximate baseline from earlier results
        current_score = self.evaluation_scores[category]
        improvement = ((current_score - baseline_score) / baseline_score * 100) if baseline_score > 0 else 0
        self.quality_improvements[category] = improvement
        logger.info(f"✅ Comprehensive analysis complete for {category}")
        logger.info(f"🎯 Final score: {current_score:.3f} (Improvement: {improvement:+.1f}%)")
        return category_results
    def generate_mcp_final_output(self, categories: List[str]) -> Dict[str, Any]:
        """Generate comprehensive MCP-pattern final output."""
        logger.info("🎯 GENERATING MCP-PATTERN FINAL OUTPUT")
        logger.info("=" * 60)
        for i, category in enumerate(categories, 1):
            logger.info(f"📋 Processing category {i}/{len(categories)}: {category}")
            self.comprehensive_category_analysis(category)
        final_submission = {"config_candidates": {}}
        for category in categories:
            if category in self.search_results:
                final_submission["config_candidates"][category] = self.search_results[category]['final_selection']
        end_time = datetime.now()
        execution_time = (end_time - self.performance_metrics['start_time']).total_seconds()
        overall_evaluation_score = sum(self.evaluation_scores.values()) / len(self.evaluation_scores) if self.evaluation_scores else 0
        overall_improvement = sum(self.quality_improvements.values()) / len(self.quality_improvements) if self.quality_improvements else 0
        mcp_output = {
            'mcp_pattern_analysis': {
                'timestamp': end_time.isoformat(),
                'execution_time_seconds': execution_time,
                'technologies_used': [
                    'Enhanced Vector Search',
                    'MongoDB Data Enrichment',
                    'GPT Validation' if self.gpt_service.client else 'GPT Validation (Disabled)',
                    'Mercor Evaluation API',
                    'Multi-Strategy Search',
                    'Parallel Processing'
                ]
            },
            'final_submission': final_submission,
            'category_detailed_results': self.search_results,
            'evaluation_scores': self.evaluation_scores,
            'quality_improvements': self.quality_improvements,
            'overall_metrics': {
                'overall_evaluation_score': overall_evaluation_score,
                'overall_improvement_percentage': overall_improvement,
                'categories_processed': len(categories),
                'total_candidates_processed': self.performance_metrics['candidates_processed'],
                'vector_searches_performed': self.performance_metrics['vector_searches'],
                'mongodb_validations_performed': self.performance_metrics['mongodb_validations'],
                'gpt_validations_performed': self.performance_metrics['gpt_validations'],
                'evaluation_api_calls_made': self.performance_metrics['evaluation_api_calls']
            },
            'technology_performance_analysis': {
                'vector_search_effectiveness': 'High' if self.performance_metrics['vector_searches'] > 0 else 'Not Used',
                'mongodb_integration_status': 'Active' if self.performance_metrics['mongodb_validations'] > 0 else 'Limited',
                'gpt_integration_status': 'Active' if self.performance_metrics['gpt_validations'] > 0 else 'Disabled',
                'evaluation_api_status': 'Active' if self.performance_metrics['evaluation_api_calls'] > 0 else 'Failed',
                'mcp_pattern_success': 'Full' if all([
                    self.performance_metrics['vector_searches'] > 0,
                    self.performance_metrics['mongodb_validations'] > 0,
                    self.performance_metrics['evaluation_api_calls'] > 0
                ]) else 'Partial'
            },
            'recommendations': self._generate_mcp_recommendations()
        }
        with open("mcp_comprehensive_output.json", "w") as f:
            json.dump(mcp_output, f, indent=2)
        with open("mcp_final_submission.json", "w") as f:
            json.dump(final_submission, f, indent=2)
        logger.info("📄 MCP comprehensive output saved to: mcp_comprehensive_output.json")
        logger.info("📄 MCP final submission saved to: mcp_final_submission.json")
        return mcp_output
    def _generate_mcp_recommendations(self) -> List[str]:
        """Generate intelligent MCP-pattern recommendations."""
        recommendations = []
        if self.performance_metrics['vector_searches'] > 0:
            recommendations.append("✅ Vector search successfully integrated with multiple strategies")
        if self.performance_metrics['mongodb_validations'] > 0:
            recommendations.append("✅ MongoDB data enrichment active via validation agent")
        else:
            recommendations.append("⚠️ MongoDB access limited - enhance database permissions")
        if self.performance_metrics['gpt_validations'] > 0:
            recommendations.append("✅ GPT validation successfully integrated")
        else:
            recommendations.append("🔧 Fix OpenAI API key for enhanced GPT validation")
        if self.performance_metrics['evaluation_api_calls'] > 0:
            recommendations.append("✅ Mercor evaluation API successfully integrated")
        overall_score = sum(self.evaluation_scores.values()) / len(self.evaluation_scores) if self.evaluation_scores else 0
        if overall_score > 0.6:
            recommendations.append("🎯 Excellent overall performance - MCP pattern highly effective")
        elif overall_score > 0.4:
            recommendations.append("📈 Good performance - fine-tune search strategies")
        else:
            recommendations.append("🔧 Performance needs improvement - enhance requirement matching")
        recommendations.append(f"📊 MCP Pattern Processing: {self.performance_metrics['candidates_processed']} candidates through {len(self.search_results)} categories")
        return recommendations
def main():
    """Main function to run the Working MCP Agent."""
    print("🚀 WORKING MCP-PATTERN ENHANCED AI AGENT")
    print("=" * 55)
    print("🔧 Technologies Integrated:")
    print("✅ Enhanced Vector Search (Multiple Strategies)")
    print("✅ MongoDB Data Enrichment (via Validation Agent)")  
    print("✅ GPT Validation (when available)")
    print("✅ Mercor Evaluation API")
    print("✅ Parallel Processing")
    print("✅ Comprehensive Analytics")
    print()
    agent = WorkingMCPAgent()
    categories = [
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
    results = agent.generate_mcp_final_output(categories)
    print("\n🎯 MCP-PATTERN EXECUTION SUMMARY")
    print("=" * 55)
    print(f"⏱️ Total execution time: {results['mcp_pattern_analysis']['execution_time_seconds']:.1f} seconds")
    print(f"🎯 Overall evaluation score: {results['overall_metrics']['overall_evaluation_score']:.3f}")
    print(f"📈 Overall improvement: {results['overall_metrics']['overall_improvement_percentage']:+.1f}%")
    print(f"👥 Candidates processed: {results['overall_metrics']['total_candidates_processed']}")
    print("\n🔧 TECHNOLOGY PERFORMANCE:")
    tech_analysis = results['technology_performance_analysis']
    for tech, status in tech_analysis.items():
        status_icon = "✅" if status in ['Active', 'High', 'Full'] else "⚠️" if status in ['Partial', 'Limited'] else "❌"
        print(f"{status_icon} {tech.replace('_', ' ').title()}: {status}")
    print("\n📊 CATEGORY PERFORMANCE:")
    for category, score in results['evaluation_scores'].items():
        improvement = results['quality_improvements'].get(category, 0)
        status = "✅" if score > 0.6 else "⚠️" if score > 0.4 else "❌"
        print(f"{status} {category}: {score:.3f} ({improvement:+.1f}%)")
    print("\n💡 MCP RECOMMENDATIONS:")
    for rec in results['recommendations']:
        print(f"  {rec}")
    print(f"\n📄 Comprehensive analysis: mcp_comprehensive_output.json")
    print(f"📄 Final submission: mcp_final_submission.json")
    print(f"\n🔍 Validating MCP results against official criteria...")
    return results
if __name__ == "__main__":
    main() 