#!/usr/bin/env python3
"""
MCP-Pattern Enhanced AI Agent
============================

Advanced agent using:
- GPT API for MongoDB query generation
- Data validation with GPT
- Mercor evaluation API validation
- Vector store semantic search
- Comprehensive final output analysis
"""

import os
import sys
import json
import asyncio
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import config
from src.services.gpt_service import GPTService
from src.services.search_service import SearchService  
from src.services.embedding_service import EmbeddingService
from src.models.candidate import CandidateProfile, SearchQuery, SearchStrategy
from src.utils.logger import get_logger
import pymongo

logger = get_logger(__name__)

class MCPEnhancedAgent:
    """
    MCP-Pattern Agent combining:
    - MongoDB intelligent querying via GPT
    - Multi-layer validation (GPT + Evaluation API)
    - Vector semantic search
    - Comprehensive analytics
    """
    
    def __init__(self):
        """Initialize all services and connections."""
        self.gpt_service = GPTService()
        self.search_service = SearchService()
        self.embedding_service = EmbeddingService()
        
        # MongoDB connection
        self.mongo_client = None
        self.mongo_db = None
        self.candidates_collection = None
        self._init_mongodb()
        
        # Performance tracking
        self.performance_metrics = {
            'mongodb_queries': 0,
            'gpt_validations': 0,
            'evaluation_api_calls': 0,
            'vector_searches': 0,
            'candidates_processed': 0,
            'validation_corrections': 0,
            'start_time': datetime.now()
        }
        
        # Results tracking
        self.search_results = {}
        self.validation_results = {}
        self.evaluation_scores = {}
        
    def _init_mongodb(self):
        """Initialize MongoDB connection."""
        try:
            mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
            self.mongo_client = pymongo.MongoClient(mongo_url)
            self.mongo_db = self.mongo_client.get_database("mercor_candidates")
            self.candidates_collection = self.mongo_db.get_collection("candidates")
            logger.info("✅ MongoDB connection established")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            
    def generate_mongodb_query_with_gpt(self, category: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Use GPT to generate optimized MongoDB queries based on job requirements."""
        
        if not self.gpt_service.client:
            # Fallback basic query
            return {"$text": {"$search": " ".join(requirements.get('must_have', []))}}
        
        prompt = f"""
        Generate a MongoDB query for finding candidates in category: {category}
        
        Requirements:
        - Must have: {requirements.get('must_have', [])}
        - Preferred: {requirements.get('preferred', [])}
        - Exclude: {requirements.get('exclude', [])}
        
        MongoDB collection has fields: name, email, summary, experience, education, skills, position, company, location, industry, linkedin_url
        
        Generate a MongoDB aggregation pipeline that:
        1. Uses text search and regex matching
        2. Scores candidates based on requirement matching
        3. Excludes unwanted candidates
        4. Sorts by relevance score
        
        Return ONLY valid JSON for the aggregation pipeline.
        """
        
        try:
            response = self.gpt_service._make_gpt_request([
                {"role": "system", "content": "You are a MongoDB query expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ], temperature=0.1, max_tokens=800)
            
            query_json = json.loads(response.strip())
            self.performance_metrics['mongodb_queries'] += 1
            logger.info(f"📊 Generated MongoDB query for {category}")
            return query_json
            
        except Exception as e:
            logger.warning(f"GPT query generation failed: {e}, using fallback")
            # Fallback query
            return [
                {"$match": {"$text": {"$search": " ".join(requirements.get('must_have', []))}}},
                {"$limit": 100}
            ]
    
    def execute_intelligent_mongodb_search(self, category: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute intelligent MongoDB search using GPT-generated queries."""
        
        # Generate optimized query
        mongo_query = self.generate_mongodb_query_with_gpt(category, requirements)
        
        try:
            if isinstance(mongo_query, list):
                # Aggregation pipeline
                results = list(self.candidates_collection.aggregate(mongo_query))
            else:
                # Simple find query
                results = list(self.candidates_collection.find(mongo_query).limit(100))
            
            logger.info(f"🔍 MongoDB search for {category}: {len(results)} candidates found")
            return results
            
        except Exception as e:
            logger.error(f"MongoDB query execution failed: {e}")
            
            # Fallback to basic text search
            fallback_query = {"$text": {"$search": " ".join(requirements.get('must_have', []))}}
            results = list(self.candidates_collection.find(fallback_query).limit(50))
            logger.info(f"🔄 Fallback search for {category}: {len(results)} candidates")
            return results
    
    def validate_candidate_with_gpt_enhanced(self, candidate: Dict[str, Any], category: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced GPT validation with detailed scoring."""
        
        if not self.gpt_service.client:
            return {
                'is_suitable': True,
                'confidence': 0.5,
                'gpt_score': 0.5,
                'reasoning': 'GPT unavailable - basic validation only',
                'validation_details': {}
            }
        
        candidate_summary = f"""
        Name: {candidate.get('name', 'N/A')}
        Summary: {candidate.get('summary', 'N/A')[:500]}
        Experience: {str(candidate.get('experience', []))[:300]}
        Education: {str(candidate.get('education', []))[:300]}
        Skills: {str(candidate.get('skills', []))[:200]}
        Position: {candidate.get('position', 'N/A')}
        Company: {candidate.get('company', 'N/A')}
        """
        
        prompt = f"""
        Validate this candidate for {category} position:
        
        CANDIDATE:
        {candidate_summary}
        
        REQUIREMENTS:
        Must Have: {requirements.get('must_have', [])}
        Preferred: {requirements.get('preferred', [])}
        Exclude: {requirements.get('exclude', [])}
        
        Analyze and return JSON with:
        {{
            "is_suitable": boolean,
            "confidence": float (0-1),
            "gpt_score": float (0-1),
            "reasoning": "detailed explanation",
            "hard_criteria_matches": ["list of matched must-have criteria"],
            "soft_criteria_matches": ["list of matched preferred criteria"],
            "exclusion_flags": ["list of exclusion criteria found"],
            "experience_relevance": float (0-1),
            "education_relevance": float (0-1),
            "skills_relevance": float (0-1),
            "overall_quality": "Excellent|Good|Fair|Poor"
        }}
        """
        
        try:
            response = self.gpt_service._make_gpt_request([
                {"role": "system", "content": "You are a technical recruiter expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ], temperature=0.2, max_tokens=1000)
            
            validation_result = json.loads(response.strip())
            self.performance_metrics['gpt_validations'] += 1
            
            logger.info(f"🔍 GPT validation complete: {validation_result.get('overall_quality', 'Unknown')} quality")
            return validation_result
            
        except Exception as e:
            logger.warning(f"GPT validation failed: {e}")
            return {
                'is_suitable': True,
                'confidence': 0.3,
                'gpt_score': 0.3,
                'reasoning': f'GPT validation error: {str(e)}',
                'validation_details': {}
            }
    
    def call_evaluation_api_enhanced(self, candidate_ids: List[str], category: str) -> Dict[str, Any]:
        """Enhanced evaluation API call with detailed response processing."""
        
        try:
            payload = {
                "config": category,
                "candidate_ids": candidate_ids
            }
            
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
                
                logger.info(f"✅ Evaluation API success for {category}: Score {eval_data.get('overallScore', 'N/A')}")
                return {
                    'success': True,
                    'overall_score': eval_data.get('overallScore', 0),
                    'detailed_scores': eval_data.get('detailed_scores', {}),
                    'raw_response': eval_data,
                    'category': category,
                    'candidate_count': len(candidate_ids)
                }
            else:
                logger.warning(f"⚠️ Evaluation API error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"API returned {response.status_code}",
                    'category': category
                }
                
        except Exception as e:
            logger.error(f"❌ Evaluation API call failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'category': category
            }
    
    def vector_semantic_search_enhanced(self, category: str, requirements: Dict[str, Any], limit: int = 50) -> List[CandidateProfile]:
        """Enhanced vector search with multiple query strategies."""
        
        all_candidates = []
        
        # Multiple query variations for better coverage
        query_variations = []
        
        # Base query
        base_terms = requirements.get('must_have', []) + requirements.get('preferred', [])
        query_variations.append(" ".join(base_terms))
        
        # Specific professional queries
        if 'PhD' in base_terms or 'doctorate' in base_terms:
            query_variations.append(f"PhD doctorate research university {category.split('.')[0]}")
        if 'MD' in base_terms or 'doctor' in base_terms:
            query_variations.append(f"MD doctor physician medical practice {category.split('.')[0]}")
        if 'JD' in base_terms or 'attorney' in base_terms:
            query_variations.append(f"JD attorney lawyer legal practice {category.split('.')[0]}")
        if 'MBA' in base_terms or 'finance' in base_terms:
            query_variations.append(f"MBA finance business {category.split('.')[0]}")
        
        for query_text in query_variations:
            try:
                search_query = SearchQuery(
                    query_text=query_text,
                    job_category=category,
                    strategy=SearchStrategy.HYBRID,
                    max_candidates=limit // len(query_variations)
                )
                
                candidates = self.search_service.search_candidates(search_query)
                all_candidates.extend(candidates)
                self.performance_metrics['vector_searches'] += 1
                
            except Exception as e:
                logger.warning(f"Vector search failed for '{query_text}': {e}")
        
        # Remove duplicates
        seen_ids = set()
        unique_candidates = []
        for candidate in all_candidates:
            if candidate.id not in seen_ids:
                seen_ids.add(candidate.id)
                unique_candidates.append(candidate)
        
        logger.info(f"🔍 Vector search for {category}: {len(unique_candidates)} unique candidates")
        return unique_candidates[:limit]
    
    def comprehensive_candidate_analysis(self, category: str) -> Dict[str, Any]:
        """Perform comprehensive multi-layer analysis for a category."""
        
        logger.info(f"🚀 Starting comprehensive analysis for {category}")
        
        # Load requirements
        requirements = {}
        try:
            with open("src/config/prompts.json", "r") as f:
                prompts_data = json.load(f)
                requirements = prompts_data.get("hard_filters", {}).get(category.replace('.yml', ''), {})
        except Exception as e:
            logger.warning(f"Could not load requirements: {e}")
        
        results = {
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'requirements': requirements,
            'mongodb_candidates': [],
            'vector_candidates': [],
            'validated_candidates': [],
            'final_selection': [],
            'performance_summary': {},
            'quality_analysis': {}
        }
        
        # Step 1: MongoDB intelligent search
        logger.info("📊 Step 1: MongoDB intelligent search")
        mongo_candidates = self.execute_intelligent_mongodb_search(category, requirements)
        results['mongodb_candidates'] = mongo_candidates[:50]  # Top 50
        
        # Step 2: Vector semantic search
        logger.info("🔍 Step 2: Vector semantic search")
        vector_candidates = self.vector_semantic_search_enhanced(category, requirements, limit=50)
        results['vector_candidates'] = [{'id': c.id, 'summary': c.summary[:200]} for c in vector_candidates]
        
        # Step 3: Combine and deduplicate candidates
        all_candidate_ids = set()
        combined_candidates = []
        
        # Add MongoDB candidates
        for candidate in mongo_candidates[:25]:
            if candidate.get('_id'):
                candidate_id = str(candidate['_id'])
                if candidate_id not in all_candidate_ids:
                    all_candidate_ids.add(candidate_id)
                    combined_candidates.append(candidate)
        
        # Add vector candidates
        for candidate in vector_candidates[:25]:
            if candidate.id not in all_candidate_ids:
                all_candidate_ids.add(candidate.id)
                # Convert to dict format
                combined_candidates.append({
                    '_id': candidate.id,
                    'name': getattr(candidate, 'name', 'N/A'),
                    'summary': candidate.summary,
                    'experience': getattr(candidate, 'experience_years', 0),
                    'score': getattr(candidate, 'relevance_score', 0.5)
                })
        
        logger.info(f"🔄 Combined {len(combined_candidates)} unique candidates")
        
        # Step 4: GPT validation for top candidates
        logger.info("🤖 Step 3: GPT validation")
        validated_candidates = []
        
        def validate_candidate(candidate):
            try:
                validation = self.validate_candidate_with_gpt_enhanced(candidate, category, requirements)
                self.performance_metrics['candidates_processed'] += 1
                return {
                    'candidate': candidate,
                    'validation': validation,
                    'combined_score': (
                        validation.get('gpt_score', 0.5) * 0.7 + 
                        candidate.get('score', 0.5) * 0.3
                    )
                }
            except Exception as e:
                logger.warning(f"Validation failed for candidate: {e}")
                return None
        
        # Parallel validation
        with ThreadPoolExecutor(max_workers=5) as executor:
            validation_futures = [executor.submit(validate_candidate, candidate) for candidate in combined_candidates[:30]]
            for future in validation_futures:
                result = future.result()
                if result:
                    validated_candidates.append(result)
        
        # Sort by combined score
        validated_candidates.sort(key=lambda x: x['combined_score'], reverse=True)
        results['validated_candidates'] = validated_candidates[:20]
        
        # Step 5: Final selection and evaluation API
        logger.info("📈 Step 4: Final selection and evaluation")
        top_candidates = validated_candidates[:10]
        candidate_ids = [str(c['candidate'].get('_id', '')) for c in top_candidates]
        
        # Call evaluation API
        evaluation_result = self.call_evaluation_api_enhanced(candidate_ids, category)
        results['evaluation_result'] = evaluation_result
        
        # Step 6: Quality analysis
        quality_metrics = {
            'high_quality_candidates': len([c for c in validated_candidates if c['validation'].get('overall_quality') == 'Excellent']),
            'suitable_candidates': len([c for c in validated_candidates if c['validation'].get('is_suitable', False)]),
            'average_confidence': sum([c['validation'].get('confidence', 0) for c in validated_candidates]) / len(validated_candidates) if validated_candidates else 0,
            'average_gpt_score': sum([c['validation'].get('gpt_score', 0) for c in validated_candidates]) / len(validated_candidates) if validated_candidates else 0,
            'evaluation_api_score': evaluation_result.get('overall_score', 0) if evaluation_result.get('success') else 0
        }
        
        results['quality_analysis'] = quality_metrics
        results['final_selection'] = candidate_ids
        
        # Update global tracking
        self.search_results[category] = results
        self.evaluation_scores[category] = evaluation_result.get('overall_score', 0)
        
        logger.info(f"✅ Comprehensive analysis complete for {category}")
        logger.info(f"📊 Quality: {quality_metrics['high_quality_candidates']} excellent, {quality_metrics['suitable_candidates']} suitable")
        logger.info(f"🎯 Evaluation score: {evaluation_result.get('overall_score', 'N/A')}")
        
        return results
    
    def generate_final_comprehensive_output(self, categories: List[str]) -> Dict[str, Any]:
        """Generate comprehensive final output with all analysis."""
        
        logger.info("🎯 GENERATING COMPREHENSIVE FINAL OUTPUT")
        logger.info("=" * 60)
        
        # Process all categories
        for category in categories:
            self.comprehensive_candidate_analysis(category)
        
        # Generate final submission
        final_submission = {"config_candidates": {}}
        
        for category in categories:
            if category in self.search_results:
                final_submission["config_candidates"][category] = self.search_results[category]['final_selection']
        
        # Calculate overall performance
        end_time = datetime.now()
        execution_time = (end_time - self.performance_metrics['start_time']).total_seconds()
        
        overall_evaluation_score = sum(self.evaluation_scores.values()) / len(self.evaluation_scores) if self.evaluation_scores else 0
        
        comprehensive_output = {
            'timestamp': end_time.isoformat(),
            'execution_time_seconds': execution_time,
            'final_submission': final_submission,
            'category_results': self.search_results,
            'evaluation_scores': self.evaluation_scores,
            'overall_evaluation_score': overall_evaluation_score,
            'performance_metrics': self.performance_metrics,
            'quality_summary': {
                'categories_processed': len(categories),
                'total_candidates_evaluated': self.performance_metrics['candidates_processed'],
                'mongodb_queries_executed': self.performance_metrics['mongodb_queries'],
                'gpt_validations_performed': self.performance_metrics['gpt_validations'],
                'evaluation_api_calls': self.performance_metrics['evaluation_api_calls'],
                'vector_searches_performed': self.performance_metrics['vector_searches']
            },
            'recommendations': self._generate_recommendations()
        }
        
        # Save detailed results
        with open("mcp_comprehensive_analysis.json", "w") as f:
            json.dump(comprehensive_output, f, indent=2)
        
        # Save final submission
        with open("mcp_final_submission.json", "w") as f:
            json.dump(final_submission, f, indent=2)
        
        logger.info("📄 Comprehensive analysis saved to: mcp_comprehensive_analysis.json")
        logger.info("📄 Final submission saved to: mcp_final_submission.json")
        
        return comprehensive_output
    
    def _generate_recommendations(self) -> List[str]:
        """Generate intelligent recommendations based on analysis."""
        recommendations = []
        
        if self.performance_metrics['gpt_validations'] > 0:
            recommendations.append("✅ GPT validation successfully integrated")
        else:
            recommendations.append("⚠️ Consider fixing OpenAI API key for enhanced validation")
        
        if self.performance_metrics['evaluation_api_calls'] > 0:
            recommendations.append("✅ Mercor evaluation API successfully integrated")
        
        avg_score = sum(self.evaluation_scores.values()) / len(self.evaluation_scores) if self.evaluation_scores else 0
        
        if avg_score > 0.6:
            recommendations.append("🎯 Strong overall performance - consider fine-tuning")
        elif avg_score > 0.4:
            recommendations.append("📈 Moderate performance - focus on hard criteria matching")
        else:
            recommendations.append("🔧 Performance needs improvement - enhance search strategies")
        
        recommendations.append(f"📊 Processed {self.performance_metrics['candidates_processed']} candidates with {self.performance_metrics['mongodb_queries']} MongoDB queries")
        
        return recommendations

def main():
    """Main function to run the MCP Enhanced Agent."""
    
    print("🚀 MCP-PATTERN ENHANCED AI AGENT")
    print("=" * 50)
    print("Features:")
    print("✅ GPT-generated MongoDB queries")
    print("✅ Multi-layer validation (GPT + Evaluation API)")  
    print("✅ Vector semantic search")
    print("✅ Comprehensive analytics")
    print()
    
    # Initialize agent
    agent = MCPEnhancedAgent()
    
    # Define categories to analyze
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
    
    # Generate comprehensive output
    results = agent.generate_final_comprehensive_output(categories)
    
    # Print summary
    print("\n🎯 MCP AGENT EXECUTION SUMMARY")
    print("=" * 50)
    print(f"⏱️ Execution time: {results['execution_time_seconds']:.1f} seconds")
    print(f"📊 Overall evaluation score: {results['overall_evaluation_score']:.3f}")
    print(f"🔍 Candidates processed: {results['performance_metrics']['candidates_processed']}")
    print(f"📈 MongoDB queries: {results['performance_metrics']['mongodb_queries']}")
    print(f"🤖 GPT validations: {results['performance_metrics']['gpt_validations']}")
    print(f"🌐 Evaluation API calls: {results['performance_metrics']['evaluation_api_calls']}")
    print(f"🔎 Vector searches: {results['performance_metrics']['vector_searches']}")
    
    print("\n📈 CATEGORY SCORES:")
    for category, score in results['evaluation_scores'].items():
        status = "✅" if score > 0.6 else "⚠️" if score > 0.4 else "❌"
        print(f"{status} {category}: {score:.3f}")
    
    print("\n💡 RECOMMENDATIONS:")
    for rec in results['recommendations']:
        print(f"  {rec}")
    
    print(f"\n📄 Detailed results: mcp_comprehensive_analysis.json")
    print(f"📄 Final submission: mcp_final_submission.json")

if __name__ == "__main__":
    main() 