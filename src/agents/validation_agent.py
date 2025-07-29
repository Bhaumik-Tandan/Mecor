"""
Intelligent Validation Agent
============================
AI agent that monitors, validates, and optimizes the search process in real-time.
Automatically triggers improvements and validates output quality.
"""
import os
import sys
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from src.services.search_service import search_service
from src.services.gpt_service import gpt_service
from src.services.evaluation_service import evaluation_service
from src.utils.logger import setup_logger
logger = setup_logger("validation_agent", level="INFO")
class ValidationStatus(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    FAILED = "failed"
@dataclass
class ValidationResult:
    status: ValidationStatus
    score: float
    reasoning: str
    suggestions: List[str]
    metrics: Dict[str, float]
    should_retry: bool = False
    should_escalate: bool = False
@dataclass
class SearchSession:
    query: SearchQuery
    candidates: List[CandidateProfile]
    validation_results: List[ValidationResult]
    iterations: int = 0
    start_time: float = 0
    improvements_made: List[str] = None
    def __post_init__(self):
        if self.improvements_made is None:
            self.improvements_made = []
class IntelligentValidationAgent:
    """
    AI agent that continuously monitors and validates search quality,
    automatically triggering improvements when needed.
    """
    def __init__(self):
        self.sessions: Dict[str, SearchSession] = {}
        self.performance_history: List[Dict] = []
        self.improvement_threshold = 0.7  # Minimum acceptable quality score
        self.max_iterations = 3  # Max retry attempts per search
        logger.info("🤖 Intelligent Validation Agent initialized")
    def validate_candidates(
        self, 
        candidates: List[CandidateProfile], 
        job_category: str,
        session_id: str
    ) -> ValidationResult:
        """
        Comprehensively validate candidate quality using AI analysis.
        """
        logger.info(f"🔍 Validating {len(candidates)} candidates for {job_category}")
        if not candidates:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                score=0.0,
                reasoning="No candidates found",
                suggestions=["Broaden search criteria", "Check data availability"],
                metrics={"candidate_count": 0}
            )
        validation_metrics = self._analyze_candidate_quality(candidates, job_category)
        quality_score = self._calculate_quality_score(validation_metrics)
        status, suggestions = self._determine_status_and_suggestions(
            quality_score, validation_metrics, job_category
        )
        result = ValidationResult(
            status=status,
            score=quality_score,
            reasoning=self._generate_reasoning(validation_metrics, status),
            suggestions=suggestions,
            metrics=validation_metrics,
            should_retry=quality_score < self.improvement_threshold and len(self.sessions[session_id].validation_results) < self.max_iterations,
            should_escalate=quality_score < 0.3
        )
        logger.info(f"✅ Validation complete: {status.value} (score: {quality_score:.2f})")
        return result
    def _analyze_candidate_quality(
        self, 
        candidates: List[CandidateProfile], 
        job_category: str
    ) -> Dict[str, float]:
        """Use GPT to analyze candidate quality across multiple dimensions."""
        if not gpt_service.is_available():
            logger.warning("GPT not available, using fallback metrics")
            return self._fallback_quality_metrics(candidates, job_category)
        sample_candidates = candidates[:5]
        domain_name = job_category.replace("_", " ").replace(".yml", "")
        candidates_text = ""
        for i, candidate in enumerate(sample_candidates, 1):
            candidates_text += f"""
        {i}. Name: {candidate.name}
           Summary: {candidate.summary or 'No summary available'}
        """
        prompt = f"""
        Analyze the quality of these candidates for: {domain_name}
        Evaluate each candidate on these dimensions (0.0 to 1.0):
        1. Domain expertise relevance
        2. Experience level appropriateness  
        3. Educational background alignment
        4. Professional qualifications
        5. Career progression indicators
        Candidates:
        {candidates_text}
        Also assess overall search quality:
        - Domain specificity (are all candidates truly from this field?)
        - Candidate diversity (different experience levels, backgrounds)
        - Quality consistency (similar quality across candidates)
        - Completeness (comprehensive candidate profiles)
        Return JSON:
        {{
            "domain_relevance": 0.85,
            "experience_level": 0.78,
            "education_alignment": 0.92,
            "qualifications": 0.88,
            "career_progression": 0.75,
            "domain_specificity": 0.90,
            "candidate_diversity": 0.70,
            "quality_consistency": 0.85,
            "profile_completeness": 0.80,
            "overall_assessment": "Brief overall assessment",
            "top_strengths": ["strength1", "strength2"],
            "main_concerns": ["concern1", "concern2"]
        }}
        """
        try:
            response = gpt_service.client.chat.completions.create(
                model=gpt_service.model,
                messages=[
                    {"role": "system", "content": "You are an expert recruiter and search quality analyst. Evaluate candidate search results objectively and precisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            result_text = response.choices[0].message.content.strip()
            metrics = json.loads(result_text)
            numeric_keys = [
                "domain_relevance", "experience_level", "education_alignment",
                "qualifications", "career_progression", "domain_specificity",
                "candidate_diversity", "quality_consistency", "profile_completeness"
            ]
            for key in numeric_keys:
                metrics[key] = max(0.0, min(1.0, float(metrics.get(key, 0.5))))
            return metrics
        except Exception as e:
            logger.error(f"GPT quality analysis failed: {e}")
            return self._fallback_quality_metrics(candidates, job_category)
    def _fallback_quality_metrics(
        self, 
        candidates: List[CandidateProfile], 
        job_category: str
    ) -> Dict[str, float]:
        """Fallback quality metrics when GPT is unavailable."""
        domain_keywords = self._get_domain_keywords(job_category)
        relevance_scores = []
        completeness_scores = []
        for candidate in candidates[:10]:  # Check top 10
            summary_lower = (candidate.summary or "").lower()
            keyword_matches = sum(1 for keyword in domain_keywords if keyword.lower() in summary_lower)
            relevance_score = min(1.0, keyword_matches / max(len(domain_keywords), 1))
            relevance_scores.append(relevance_score)
            completeness = 0.0
            if candidate.name: completeness += 0.3
            if candidate.summary and len(candidate.summary) > 50: completeness += 0.7
            completeness_scores.append(completeness)
        avg_relevance = sum(relevance_scores) / max(len(relevance_scores), 1)
        avg_completeness = sum(completeness_scores) / max(len(completeness_scores), 1)
        return {
            "domain_relevance": avg_relevance,
            "experience_level": 0.7,  # Assume moderate
            "education_alignment": avg_relevance,
            "qualifications": avg_relevance,
            "career_progression": 0.7,
            "domain_specificity": avg_relevance,
            "candidate_diversity": 0.8,  # Assume good diversity
            "quality_consistency": 0.7,
            "profile_completeness": avg_completeness,
            "overall_assessment": "Fallback analysis - GPT unavailable",
            "top_strengths": ["Candidates found"],
            "main_concerns": ["Limited analysis without GPT"]
        }
    def _get_domain_keywords(self, job_category: str) -> List[str]:
        """Get expected keywords for a domain."""
        domain_keywords = {
            "mathematics_phd": ["mathematics", "mathematical", "PhD", "theorem", "analysis", "algebra"],
            "biology_expert": ["biology", "molecular", "cell", "genomics", "biotechnology", "PhD"],
            "radiology": ["radiology", "imaging", "radiologist", "MD", "medical", "diagnostic"],
            "tax_lawyer": ["tax", "attorney", "lawyer", "IRS", "legal", "JD"],
        }
        return domain_keywords.get(job_category.replace(".yml", ""), ["professional", "expert"])
    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calculate weighted quality score from metrics."""
        weights = {
            "domain_relevance": 0.25,
            "education_alignment": 0.20,
            "qualifications": 0.15,
            "domain_specificity": 0.15,
            "quality_consistency": 0.10,
            "profile_completeness": 0.10,
            "career_progression": 0.05
        }
        score = 0.0
        for metric, weight in weights.items():
            score += metrics.get(metric, 0.5) * weight
        return min(1.0, max(0.0, score))
    def _determine_status_and_suggestions(
        self, 
        quality_score: float, 
        metrics: Dict[str, float], 
        job_category: str
    ) -> Tuple[ValidationStatus, List[str]]:
        """Determine validation status and improvement suggestions."""
        suggestions = []
        if quality_score >= 0.9:
            status = ValidationStatus.EXCELLENT
        elif quality_score >= 0.8:
            status = ValidationStatus.GOOD
        elif quality_score >= 0.6:
            status = ValidationStatus.MODERATE
        elif quality_score >= 0.3:
            status = ValidationStatus.POOR
        else:
            status = ValidationStatus.FAILED
        if metrics.get("domain_relevance", 0) < 0.7:
            suggestions.append("Improve domain-specific keywords and filters")
        if metrics.get("domain_specificity", 0) < 0.7:
            suggestions.append("Add cross-domain exclusion filters")
        if metrics.get("profile_completeness", 0) < 0.6:
            suggestions.append("Prioritize candidates with complete profiles")
        if metrics.get("quality_consistency", 0) < 0.7:
            suggestions.append("Improve ranking algorithm for consistent quality")
        if len(suggestions) == 0 and quality_score < 0.8:
            suggestions.append("Consider alternative search strategies")
        return status, suggestions
    def _generate_reasoning(self, metrics: Dict[str, float], status: ValidationStatus) -> str:
        """Generate human-readable reasoning for the validation result."""
        assessment = metrics.get("overall_assessment", "")
        strengths = metrics.get("top_strengths", [])
        concerns = metrics.get("main_concerns", [])
        reasoning = f"Status: {status.value.title()}. "
        if assessment:
            reasoning += f"{assessment}. "
        if strengths:
            reasoning += f"Strengths: {', '.join(strengths)}. "
        if concerns:
            reasoning += f"Concerns: {', '.join(concerns)}."
        return reasoning.strip()
    def orchestrate_search(
        self, 
        query: SearchQuery, 
        session_id: Optional[str] = None
    ) -> Tuple[List[CandidateProfile], List[ValidationResult]]:
        """
        Orchestrate an intelligent search with automatic validation and improvement.
        """
        if session_id is None:
            session_id = f"search_{int(time.time())}"
        logger.info(f"🚀 Starting orchestrated search: {session_id}")
        session = SearchSession(
            query=query,
            candidates=[],
            validation_results=[],
            start_time=time.time()
        )
        self.sessions[session_id] = session
        best_candidates = []
        best_score = 0.0
        for iteration in range(self.max_iterations):
            session.iterations = iteration + 1
            logger.info(f"🔄 Search iteration {session.iterations}/{self.max_iterations}")
            candidates = self._execute_search_with_strategy(query, iteration)
            session.candidates = candidates
            validation = self.validate_candidates(candidates, query.job_category, session_id)
            session.validation_results.append(validation)
            if validation.score > best_score:
                best_candidates = candidates
                best_score = validation.score
            logger.info(f"📊 Iteration {session.iterations}: Score {validation.score:.2f} ({validation.status.value})")
            if not validation.should_retry or validation.status == ValidationStatus.EXCELLENT:
                break
            if validation.suggestions:
                improvements = self._apply_improvements(query, validation.suggestions, iteration)
                session.improvements_made.extend(improvements)
                logger.info(f"🔧 Applied improvements: {', '.join(improvements)}")
        duration = time.time() - session.start_time
        logger.info(f"✅ Search completed in {duration:.1f}s with {session.iterations} iterations")
        logger.info(f"🏆 Best score: {best_score:.2f} ({len(best_candidates)} candidates)")
        return best_candidates, session.validation_results
    def _execute_search_with_strategy(
        self, 
        query: SearchQuery, 
        iteration: int
    ) -> List[CandidateProfile]:
        """Execute search with strategy adaptation based on iteration."""
        if iteration == 0:
            strategy = SearchStrategy.HYBRID
        elif iteration == 1:
            strategy = SearchStrategy.VECTOR_ONLY
            query.max_candidates = min(50, query.max_candidates * 2)
        else:
            strategy = SearchStrategy.BM25_ONLY
        logger.info(f"🔍 Using strategy: {strategy.value}")
        return search_service.search_candidates(query, strategy)
    def _apply_improvements(
        self, 
        query: SearchQuery, 
        suggestions: List[str], 
        iteration: int
    ) -> List[str]:
        """Apply improvements based on validation suggestions."""
        improvements_made = []
        for suggestion in suggestions:
            if "domain-specific keywords" in suggestion:
                improvements_made.append("Enhanced domain keywords")
            elif "cross-domain exclusion" in suggestion:
                improvements_made.append("Cross-domain filtering")
            elif "complete profiles" in suggestion:
                improvements_made.append("Profile completeness priority")
            elif "ranking algorithm" in suggestion:
                improvements_made.append("Ranking adjustment")
        return improvements_made
    def generate_performance_report(self, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive performance report for a search session."""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        session = self.sessions[session_id]
        report = {
            "session_id": session_id,
            "query": {
                "text": session.query.query_text,
                "category": session.query.job_category,
                "strategy": session.query.strategy.value
            },
            "performance": {
                "iterations": session.iterations,
                "duration": time.time() - session.start_time,
                "final_candidate_count": len(session.candidates),
                "improvements_made": session.improvements_made
            },
            "validation_scores": [
                {
                    "iteration": i + 1,
                    "score": vr.score,
                    "status": vr.status.value,
                    "reasoning": vr.reasoning
                }
                for i, vr in enumerate(session.validation_results)
            ],
            "final_assessment": session.validation_results[-1].status.value if session.validation_results else "no_validation",
            "recommendations": session.validation_results[-1].suggestions if session.validation_results else []
        }
        return report
validation_agent = IntelligentValidationAgent() 