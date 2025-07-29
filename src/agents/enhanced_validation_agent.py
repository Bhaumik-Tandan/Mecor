#!/usr/bin/env python3
"""
Enhanced AI Validation Agent
============================

Advanced candidate validation with LinkedIn verification, 
MongoDB cross-reference, and quality scoring.
"""

import os
import sys
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.models.candidate import CandidateProfile
from src.services.gpt_service import gpt_service
from src.utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv()

class EnhancedValidationAgent:
    """Advanced AI agent for candidate validation and quality scoring."""
    
    def __init__(self):
        self.mongo_url = os.getenv('MONGO_URL')
        self.db_name = "interview_data"
        self.collection_name = "linkedin_data_subset"
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.85,
            'good': 0.70,
            'acceptable': 0.55,
            'poor': 0.40
        }
        
        # Evaluation score thresholds
        self.evaluation_thresholds = {
            'target_score': 0.80,
            'minimum_acceptable': 0.60,
            'rerun_threshold': 0.50
        }
        
        logger.info("Enhanced Validation Agent initialized")
    
    def get_mongo_collection(self):
        """Get MongoDB collection for validation."""
        if not self.mongo_url:
            logger.warning("MongoDB URL not configured")
            return None
            
        try:
            client = MongoClient(self.mongo_url, tlsCAFile=certifi.where())
            return client[self.db_name][self.collection_name]
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return None
    
    def validate_candidate_with_mongodb(self, candidate: CandidateProfile) -> Dict[str, Any]:
        """Cross-validate candidate against original MongoDB data."""
        collection = self.get_mongo_collection()
        if not collection:
            return {"validated": False, "error": "MongoDB not available"}
        
        try:
            # Find candidate in MongoDB
            mongo_doc = collection.find_one({"_id": candidate.id})
            
            if not mongo_doc:
                return {
                    "validated": False,
                    "error": "Candidate not found in MongoDB",
                    "data_integrity": False
                }
            
            # Validate data consistency
            validation_result = {
                "validated": True,
                "data_integrity": True,
                "consistency_score": 0.0,
                "issues": []
            }
            
            # Check name consistency
            mongo_name = mongo_doc.get('name', '').strip()
            if mongo_name and candidate.name:
                name_similarity = self._calculate_string_similarity(mongo_name, candidate.name)
                if name_similarity < 0.8:
                    validation_result["issues"].append(f"Name mismatch: MongoDB='{mongo_name}', Candidate='{candidate.name}'")
                else:
                    validation_result["consistency_score"] += 0.3
            
            # Check email consistency
            mongo_email = mongo_doc.get('email', '').strip()
            if mongo_email and candidate.email:
                if mongo_email.lower() != candidate.email.lower():
                    validation_result["issues"].append(f"Email mismatch: MongoDB='{mongo_email}', Candidate='{candidate.email}'")
                else:
                    validation_result["consistency_score"] += 0.2
            
            # Check LinkedIn ID consistency
            mongo_linkedin_id = mongo_doc.get('linkedinId', '').strip()
            if mongo_linkedin_id and candidate.linkedin_id:
                if mongo_linkedin_id != candidate.linkedin_id:
                    validation_result["issues"].append(f"LinkedIn ID mismatch")
                else:
                    validation_result["consistency_score"] += 0.2
            
            # Check summary consistency
            mongo_summary = mongo_doc.get('rerankSummary', '').strip()
            if mongo_summary and candidate.summary:
                summary_similarity = self._calculate_string_similarity(mongo_summary, candidate.summary)
                if summary_similarity < 0.7:
                    validation_result["issues"].append("Summary content mismatch")
                else:
                    validation_result["consistency_score"] += 0.3
            
            # Add MongoDB metadata
            validation_result["mongo_metadata"] = {
                "has_embedding": bool(mongo_doc.get('embedding')),
                "country": mongo_doc.get('country', ''),
                "linkedin_id": mongo_linkedin_id,
                "summary_length": len(mongo_summary) if mongo_summary else 0
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"MongoDB validation failed for {candidate.id}: {e}")
            return {
                "validated": False,
                "error": f"Validation error: {e}",
                "data_integrity": False
            }
    
    def enhanced_linkedin_validation(self, candidate: CandidateProfile) -> Dict[str, Any]:
        """Advanced LinkedIn profile validation."""
        linkedin_result = {
            "is_valid": False,
            "completeness_score": 0.0,
            "quality_indicators": [],
            "issues": []
        }
        
        # Check LinkedIn ID format
        if candidate.linkedin_id:
            # LinkedIn IDs are typically alphanumeric strings
            if re.match(r'^[a-zA-Z0-9\-_]+$', candidate.linkedin_id):
                linkedin_result["quality_indicators"].append("Valid LinkedIn ID format")
                linkedin_result["completeness_score"] += 0.4
                linkedin_result["is_valid"] = True
            else:
                linkedin_result["issues"].append("Invalid LinkedIn ID format")
        
        # Check LinkedIn URL if available
        if candidate.linkedin_url:
            if candidate.is_linkedin_valid():
                linkedin_result["quality_indicators"].append("Valid LinkedIn URL")
                linkedin_result["completeness_score"] += 0.3
                linkedin_result["is_valid"] = True
            else:
                linkedin_result["issues"].append("Invalid LinkedIn URL format")
        
        # Check for LinkedIn indicators in summary
        if candidate.summary:
            linkedin_indicators = [
                'linkedin', 'professional network', 'connections',
                'endorsements', 'recommendations', 'profile'
            ]
            
            summary_lower = candidate.summary.lower()
            found_indicators = [ind for ind in linkedin_indicators if ind in summary_lower]
            
            if found_indicators:
                linkedin_result["quality_indicators"].append(f"LinkedIn context in summary: {', '.join(found_indicators)}")
                linkedin_result["completeness_score"] += 0.3
        
        return linkedin_result
    
    def validate_candidate_quality(self, candidate: CandidateProfile) -> Dict[str, Any]:
        """Comprehensive candidate quality validation."""
        
        # Basic quality score from the candidate model
        base_quality = candidate.calculate_quality_score()
        
        # Enhanced validation checks
        quality_result = {
            "base_quality_score": base_quality,
            "enhanced_score": base_quality,
            "quality_level": "",
            "validation_details": {
                "linkedin": {},
                "mongodb": {},
                "experience": {},
                "profile_completeness": {}
            },
            "recommendations": []
        }
        
        # LinkedIn validation
        linkedin_validation = self.enhanced_linkedin_validation(candidate)
        quality_result["validation_details"]["linkedin"] = linkedin_validation
        
        # MongoDB cross-validation
        mongodb_validation = self.validate_candidate_with_mongodb(candidate)
        quality_result["validation_details"]["mongodb"] = mongodb_validation
        
        # Experience validation
        exp_years = candidate.estimate_experience_years()
        experience_validation = {
            "estimated_years": exp_years,
            "experience_level": self._classify_experience_level(exp_years),
            "experience_indicators": self._extract_experience_indicators(candidate.summary or "")
        }
        quality_result["validation_details"]["experience"] = experience_validation
        
        # Profile completeness validation
        completeness = self._validate_profile_completeness(candidate)
        quality_result["validation_details"]["profile_completeness"] = completeness
        
        # Calculate enhanced score
        enhanced_score = base_quality
        
        # LinkedIn bonus
        if linkedin_validation["is_valid"]:
            enhanced_score += 0.1 * linkedin_validation["completeness_score"]
        
        # MongoDB consistency bonus
        if mongodb_validation.get("validated") and mongodb_validation.get("data_integrity"):
            enhanced_score += 0.05 * mongodb_validation.get("consistency_score", 0)
        
        # Experience clarity bonus
        if exp_years >= 2:
            enhanced_score += 0.05
        
        quality_result["enhanced_score"] = min(1.0, enhanced_score)
        
        # Determine quality level
        if enhanced_score >= self.quality_thresholds['excellent']:
            quality_result["quality_level"] = "excellent"
        elif enhanced_score >= self.quality_thresholds['good']:
            quality_result["quality_level"] = "good"
        elif enhanced_score >= self.quality_thresholds['acceptable']:
            quality_result["quality_level"] = "acceptable"
        else:
            quality_result["quality_level"] = "poor"
        
        # Generate recommendations
        quality_result["recommendations"] = self._generate_quality_recommendations(
            candidate, linkedin_validation, mongodb_validation, experience_validation
        )
        
        return quality_result
    
    def validate_candidate_list(
        self, 
        candidates: List[CandidateProfile], 
        job_category: str
    ) -> Dict[str, Any]:
        """Validate entire candidate list with quality thresholds."""
        
        validation_results = []
        quality_scores = []
        
        for candidate in candidates:
            validation = self.validate_candidate_quality(candidate)
            validation_results.append({
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "validation": validation
            })
            quality_scores.append(validation["enhanced_score"])
        
        # Calculate aggregate metrics
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        quality_distribution = {
            "excellent": sum(1 for score in quality_scores if score >= self.quality_thresholds['excellent']),
            "good": sum(1 for score in quality_scores if self.quality_thresholds['good'] <= score < self.quality_thresholds['excellent']),
            "acceptable": sum(1 for score in quality_scores if self.quality_thresholds['acceptable'] <= score < self.quality_thresholds['good']),
            "poor": sum(1 for score in quality_scores if score < self.quality_thresholds['acceptable'])
        }
        
        # Determine if list meets quality standards
        meets_standards = (
            avg_quality >= self.quality_thresholds['acceptable'] and
            quality_distribution['poor'] <= len(candidates) * 0.2  # Max 20% poor quality
        )
        
        return {
            "job_category": job_category,
            "total_candidates": len(candidates),
            "average_quality_score": avg_quality,
            "quality_distribution": quality_distribution,
            "meets_quality_standards": meets_standards,
            "recommendations": self._generate_list_recommendations(quality_distribution, avg_quality),
            "candidate_validations": validation_results,
            "quality_thresholds": self.quality_thresholds
        }
    
    def should_rerun_search(self, evaluation_score: float, quality_score: float) -> Tuple[bool, str]:
        """Determine if search should be rerun based on evaluation and quality scores."""
        
        if evaluation_score < self.evaluation_thresholds['rerun_threshold']:
            return True, f"Evaluation score {evaluation_score:.3f} below rerun threshold {self.evaluation_thresholds['rerun_threshold']}"
        
        if quality_score < self.quality_thresholds['acceptable']:
            return True, f"Quality score {quality_score:.3f} below acceptable threshold {self.quality_thresholds['acceptable']}"
        
        if evaluation_score < self.evaluation_thresholds['minimum_acceptable'] and quality_score < self.quality_thresholds['good']:
            return True, f"Both evaluation ({evaluation_score:.3f}) and quality ({quality_score:.3f}) scores are concerning"
        
        return False, "Scores meet quality standards"
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        if not str1 or not str2:
            return 0.0
        
        # Simple similarity based on common words
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _classify_experience_level(self, years: int) -> str:
        """Classify experience level based on years."""
        if years >= 10:
            return "senior"
        elif years >= 5:
            return "mid-level"
        elif years >= 2:
            return "junior"
        else:
            return "entry-level"
    
    def _extract_experience_indicators(self, summary: str) -> List[str]:
        """Extract experience indicators from summary."""
        if not summary:
            return []
        
        indicators = []
        summary_lower = summary.lower()
        
        # Look for leadership indicators
        leadership_terms = ['led', 'managed', 'directed', 'supervised', 'oversaw', 'headed']
        for term in leadership_terms:
            if term in summary_lower:
                indicators.append(f"Leadership: {term}")
        
        # Look for achievement indicators
        achievement_terms = ['achieved', 'improved', 'increased', 'reduced', 'delivered', 'implemented']
        for term in achievement_terms:
            if term in summary_lower:
                indicators.append(f"Achievement: {term}")
        
        # Look for skill indicators
        skill_terms = ['expertise', 'proficient', 'skilled', 'experienced', 'specialist']
        for term in skill_terms:
            if term in summary_lower:
                indicators.append(f"Skill: {term}")
        
        return indicators[:10]  # Limit to top 10
    
    def _validate_profile_completeness(self, candidate: CandidateProfile) -> Dict[str, Any]:
        """Validate profile completeness."""
        completeness = {
            "required_fields_present": 0,
            "optional_fields_present": 0,
            "completeness_percentage": 0.0,
            "missing_fields": [],
            "present_fields": []
        }
        
        # Required fields
        required_fields = [
            ("name", candidate.name),
            ("summary", candidate.summary)
        ]
        
        for field_name, field_value in required_fields:
            if field_value and len(str(field_value).strip()) > 0:
                completeness["required_fields_present"] += 1
                completeness["present_fields"].append(field_name)
            else:
                completeness["missing_fields"].append(field_name)
        
        # Optional fields
        optional_fields = [
            ("email", candidate.email),
            ("linkedin_id", candidate.linkedin_id),
            ("linkedin_url", candidate.linkedin_url),
            ("country", candidate.country)
        ]
        
        for field_name, field_value in optional_fields:
            if field_value and len(str(field_value).strip()) > 0:
                completeness["optional_fields_present"] += 1
                completeness["present_fields"].append(field_name)
        
        total_fields = len(required_fields) + len(optional_fields)
        present_fields = completeness["required_fields_present"] + completeness["optional_fields_present"]
        completeness["completeness_percentage"] = (present_fields / total_fields) * 100
        
        return completeness
    
    def _generate_quality_recommendations(
        self, 
        candidate: CandidateProfile, 
        linkedin_validation: Dict, 
        mongodb_validation: Dict, 
        experience_validation: Dict
    ) -> List[str]:
        """Generate recommendations for improving candidate quality."""
        recommendations = []
        
        if not linkedin_validation["is_valid"]:
            recommendations.append("Verify LinkedIn profile completeness and validity")
        
        if not mongodb_validation.get("validated"):
            recommendations.append("Cross-reference with original data source")
        
        if experience_validation["estimated_years"] < 2:
            recommendations.append("Verify minimum experience requirements")
        
        if not candidate.email:
            recommendations.append("Obtain valid email contact information")
        
        if not candidate.summary or len(candidate.summary) < 100:
            recommendations.append("Enhance profile summary with more detailed information")
        
        return recommendations
    
    def _generate_list_recommendations(
        self, 
        quality_distribution: Dict[str, int], 
        avg_quality: float
    ) -> List[str]:
        """Generate recommendations for candidate list improvement."""
        recommendations = []
        
        if avg_quality < self.quality_thresholds['good']:
            recommendations.append("Consider refining search criteria to improve overall quality")
        
        if quality_distribution['poor'] > quality_distribution['excellent']:
            recommendations.append("Filter out low-quality candidates and search for higher-quality alternatives")
        
        if quality_distribution['excellent'] == 0:
            recommendations.append("Expand search to find more highly qualified candidates")
        
        return recommendations 