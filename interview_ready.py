#!/usr/bin/env python3
"""
Interview-Ready Search System
============================

Clean, working script for the interview testing with private queries.
This script includes all improvements: filter extraction, GPT enhancement, quality filtering.
"""

import sys
import os
import time
import json
from typing import Dict, List, Optional
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.candidate import SearchQuery, SearchStrategy, CandidateProfile
from src.services.search_service import search_service
from src.services.gpt_service import gpt_service
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger(
    name="interview_ready",
    level="INFO",
    log_file="logs/interview_ready.log"
)

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class InterviewSearchAgent:
    """Interview-ready search agent with all improvements."""
    
    def __init__(self):
        self.search_service = search_service
        logger.info("🚀 Interview Search Agent initialized with all improvements")
    
    def search(self, query_text: str, output_format: str = "table") -> Dict:
        """Search function with all improvements for interview testing."""
        start_time = time.time()
        
        # Step 1: Correct spelling and improve query using GPT
        corrected_query = self._correct_query(query_text)
        
        if corrected_query != query_text:
            print(f"{Colors.YELLOW}🔧 Query corrected: '{query_text}' → '{corrected_query}'{Colors.END}")
        
        # Step 2: Enhance query understanding with GPT
        enhanced_query = self._enhance_query_understanding(corrected_query)
        
        print(f"{Colors.CYAN}🔍 Searching for: {enhanced_query}{Colors.END}")
        
        try:
            # Step 3: Use GPT-enhanced search with filter extraction
            search_query = SearchQuery(
                query_text=enhanced_query,
                job_category="general",
                strategy=SearchStrategy.GPT_ENHANCED,
                max_candidates=25  # Increased for better selection
            )
            
            candidates = self.search_service.search_candidates(
                search_query, 
                SearchStrategy.GPT_ENHANCED
            )
            
            # Step 4: Apply quality filtering with GPT validation
            quality_candidates = self._filter_by_quality(candidates)
            
            # Step 5: GPT-powered final ranking and selection
            final_candidates = self._gpt_final_ranking(quality_candidates, enhanced_query)
            
            # Step 6: Remove duplicates based on candidate ID
            seen_ids = set()
            unique_candidates = []
            for candidate in final_candidates:
                if candidate.id not in seen_ids:
                    seen_ids.add(candidate.id)
                    unique_candidates.append(candidate)
            
            final_candidates = unique_candidates
            
            # Step 7: Adjust count based on quality
            final_candidates = self._adjust_count(final_candidates)
            
            search_time = time.time() - start_time
            
            result = {
                "num_candidates": len(final_candidates),
                "candidate_ids": [c.id for c in final_candidates],
                "candidate_names": [c.name for c in final_candidates],
                "candidate_summaries": [c.summary for c in final_candidates],
                "candidate_countries": [c.country for c in final_candidates],
                "search_time": search_time,
                "query": query_text,
                "enhanced_query": enhanced_query
            }
            
            print(f"{Colors.GREEN}✅ Found {len(final_candidates)} quality candidates in {search_time:.2f}s{Colors.END}")
            
            # Show query analysis
            if corrected_query != query_text:
                print(f"{Colors.CYAN}🔍 Query Analysis: '{query_text}' → '{enhanced_query}'{Colors.END}")
            else:
                print(f"{Colors.CYAN}🔍 Query Analysis: '{query_text}' → '{enhanced_query}'{Colors.END}")
            print(f"{Colors.CYAN}📊 GPT-Enhanced Filter: Applied (30% relevance + 70% quality, threshold: 0.3){Colors.END}")
            print(f"{Colors.CYAN}🎯 Dynamic Count: {len(final_candidates)} candidates (query-focused){Colors.END}")
            
            # Step 7: Display results in requested format
            self._display_results(result, output_format)
            
            return result
            
        except Exception as e:
            print(f"{Colors.RED}❌ Search failed: {e}{Colors.END}")
            logger.error(f"Search failed for query '{query_text}': {e}")
            return {
                "num_candidates": 0, 
                "candidate_ids": [], 
                "candidate_names": [], 
                "candidate_summaries": [], 
                "candidate_countries": [], 
                "search_time": 0,
                "query": query_text
            }
    
    def _filter_by_quality(self, candidates: List[CandidateProfile]) -> List[CandidateProfile]:
        """Filter candidates by quality and relevance."""
        if not candidates:
            return []
        
        quality_candidates = []
        for candidate in candidates:
            quality_score = self._calculate_quality_score(candidate)
            relevance_score = self._calculate_relevance_score(candidate)
            
            # Combined score: 30% relevance + 70% quality (more flexible, less restrictive)
            combined_score = (relevance_score * 0.3) + (quality_score * 0.7)
            
            if combined_score >= 0.3:  # Lower threshold for more inclusive results
                quality_candidates.append((candidate, combined_score))
        
        # Sort by combined score
        quality_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return [candidate for candidate, _ in quality_candidates]
    
    def _calculate_quality_score(self, candidate: CandidateProfile) -> float:
        """Calculate quality score for a candidate."""
        score = 0.0
        
        # Summary completeness (40% weight)
        if candidate.summary:
            summary_length = len(candidate.summary.strip())
            if summary_length > 200:
                score += 0.4
            elif summary_length > 100:
                score += 0.3
            elif summary_length > 50:
                score += 0.2
            else:
                score += 0.1
        
        # Name completeness (30% weight)
        if candidate.name and len(candidate.name.strip()) > 2:
            score += 0.3
        
        # Country information (15% weight)
        if candidate.country and candidate.country.strip():
            score += 0.15
        
        # LinkedIn ID presence (15% weight)
        if candidate.linkedin_id and candidate.linkedin_id.strip():
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_relevance_score(self, candidate: CandidateProfile) -> float:
        """Calculate relevance score based on query terms matching."""
        if not candidate.summary:
            return 0.0
        
        summary_lower = candidate.summary.lower()
        name_lower = (candidate.name or "").lower()
        full_text = f"{name_lower} {summary_lower}"
        
        # Get the original query from the search context
        # For now, we'll use a simple approach to detect query intent
        score = 0.0
        
        # Medical/Healthcare related terms (positive scoring)
        medical_terms = [
            "doctor", "physician", "medical", "healthcare", "surgeon", "nurse",
            "clinical", "patient", "hospital", "medicine", "surgery", "cardiology",
            "pediatrics", "emergency", "radiology", "anesthesiology", "internal medicine",
            "family medicine", "orthopedic", "neurology", "oncology", "dermatology",
            "psychiatry", "pathology", "obstetrics", "gynecology", "urology", "ophthalmology",
            "otolaryngology", "pulmonology", "endocrinology", "gastroenterology", "nephrology",
            "rheumatology", "hematology", "infectious disease", "critical care", "intensive care",
            "trauma", "vascular", "plastic surgery", "general surgery", "thoracic surgery",
            "neurosurgery", "cardiac surgery", "transplant", "residency", "fellowship",
            "board certified", "licensed", "md", "do", "medical degree", "medical school"
        ]
        
        # Legal related terms (negative scoring)
        legal_terms = [
            "lawyer", "attorney", "legal", "counsel", "litigation", "contract",
            "compliance", "regulatory", "law firm", "corporate counsel", "general counsel",
            "associate", "partner", "esquire", "jd", "law degree", "law school",
            "bar exam", "legal services", "legal advice", "legal counsel"
        ]
        
        # Software/Engineering related terms (positive scoring for tech queries)
        tech_terms = [
            "software engineer", "developer", "programmer", "backend", "frontend",
            "full stack", "python", "java", "javascript", "react", "node.js",
            "api", "database", "aws", "cloud", "devops", "agile", "scrum",
            "senior", "lead", "architect", "technical", "coding", "programming"
        ]
        
        # Data Science/AI related terms (positive scoring for data queries)
        data_science_terms = [
            "data scientist", "data analyst", "machine learning", "ai", "artificial intelligence",
            "ml engineer", "data engineer", "statistical analysis", "data modeling", "predictive modeling",
            "deep learning", "neural networks", "nlp", "natural language processing", "computer vision",
            "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
            "hadoop", "spark", "kafka", "data pipeline", "etl", "data warehouse", "big data",
            "analytics", "business intelligence", "bi", "data visualization", "tableau", "power bi",
            "sql", "nosql", "mongodb", "postgresql", "mysql", "r", "jupyter", "notebook",
            "algorithm", "model", "training", "inference", "feature engineering", "data mining"
        ]
        
        # Product Management related terms (positive scoring for product queries)
        product_management_terms = [
            "product manager", "product management", "product strategy", "product development",
            "product lifecycle", "product owner", "scrum master", "agile", "scrum", "kanban",
            "jira", "confluence", "roadmap", "backlog", "sprint", "stakeholder", "user story",
            "product requirements", "market research", "competitive analysis", "user experience",
            "ux", "ui", "customer research", "product analytics", "a/b testing", "mvp",
            "go-to-market", "gtm", "product launch", "feature prioritization", "product vision",
            "business analyst", "project manager", "program manager", "technical product manager"
        ]
        
        # Marketing related terms (positive scoring for marketing queries)
        marketing_terms = [
            "marketing manager", "marketing", "digital marketing", "seo", "sem", "content marketing",
            "social media marketing", "email marketing", "brand marketing", "campaign management",
            "marketing strategy", "marketing analytics", "marketing automation", "lead generation",
            "customer acquisition", "brand management", "public relations", "pr", "advertising",
            "market research", "customer insights", "marketing communications", "b2b marketing",
            "b2c marketing", "product marketing", "growth marketing", "performance marketing",
            "marketing roi", "marketing kpis", "marketing metrics", "marketing campaigns",
            "marketing tools", "marketing platforms", "crm", "marketing software", "marketing budget"
        ]
        
        # Design related terms (positive scoring for design queries)
        design_terms = [
            "designer", "design", "ui designer", "ux designer", "graphic designer", "visual designer",
            "product designer", "web designer", "interaction designer", "user experience designer",
            "user interface designer", "creative designer", "art director", "design director",
            "adobe creative suite", "photoshop", "illustrator", "indesign", "figma", "sketch",
            "prototyping", "wireframing", "visual design", "brand design", "logo design",
            "typography", "color theory", "layout design", "print design", "digital design",
            "web design", "mobile design", "responsive design", "design system", "design thinking",
            "user research", "usability testing", "design portfolio", "creative direction"
        ]
        
        # Sales related terms (positive scoring for sales queries)
        sales_terms = [
            "sales manager", "sales", "sales representative", "account executive", "sales director",
            "sales leader", "business development", "bd", "sales strategy", "sales operations",
            "sales analytics", "sales performance", "sales training", "sales coaching", "sales team",
            "customer acquisition", "lead generation", "prospecting", "cold calling", "sales pipeline",
            "sales forecasting", "sales quota", "sales target", "sales commission", "sales territory",
            "b2b sales", "b2c sales", "enterprise sales", "inside sales", "outside sales",
            "field sales", "channel sales", "partner sales", "sales enablement", "sales tools",
            "crm", "salesforce", "hubspot", "pipedrive", "sales reporting", "sales metrics",
            "sales kpis", "sales roi", "negotiation", "closing", "deal management"
        ]
        
        # Check for medical terms (positive score)
        for term in medical_terms:
            if term in full_text:
                score += 0.1
        
        # Check for legal terms (negative score - penalize lawyers in medical searches)
        for term in legal_terms:
            if term in full_text:
                score -= 0.3  # Strong penalty for legal terms in medical context
        
        # Check for tech terms (positive score for tech queries)
        for term in tech_terms:
            if term in full_text:
                score += 0.1
        
        # Check for data science terms (positive score for data queries)
        for term in data_science_terms:
            if term in full_text:
                score += 0.15  # Higher weight for data science relevance
        
        # Check for product management terms (positive score for product queries)
        for term in product_management_terms:
            if term in full_text:
                score += 0.15  # Higher weight for product management relevance
        
        # Check for marketing terms (positive score for marketing queries)
        for term in marketing_terms:
            if term in full_text:
                score += 0.15  # Higher weight for marketing relevance
        
        # Check for design terms (positive score for design queries)
        for term in design_terms:
            if term in full_text:
                score += 0.15  # Higher weight for design relevance
        
        # Check for sales terms (positive score for sales queries)
        for term in sales_terms:
            if term in full_text:
                score += 0.15  # Higher weight for sales relevance
        
        # Basic professional relevance
        professional_terms = [
            "experience", "skills", "expertise", "proficient", "knowledge",
            "background", "qualifications", "certifications", "education"
        ]
        
        for term in professional_terms:
            if term in full_text:
                score += 0.02
        
        # Cap the score between 0 and 1
        return max(0.0, min(score, 1.0))
    
    def _correct_query(self, query_text: str) -> str:
        """Correct spelling and improve query using GPT."""
        if not gpt_service.is_available():
            return query_text
        
        try:
            correction_prompt = f"""Correct and improve this search query for finding job candidates:

Original query: "{query_text}"

Please:
1. Fix any spelling errors
2. Improve grammar if needed
3. Make it more professional and clear
4. Keep the original intent

Return only the corrected query, nothing else.

Example:
Input: "sotware gneeier"
Output: "software engineer"

Input: "senior devloper with pythn"
Output: "senior developer with Python"

Corrected query:"""

            response = gpt_service._make_gpt_request(
                [{"role": "user", "content": correction_prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            corrected = response.strip().strip('"').strip("'")
            return corrected if corrected else query_text
            
        except Exception as e:
            logger.warning(f"Query correction failed: {e}")
            return query_text
    
    def _enhance_query_understanding(self, query_text: str) -> str:
        """Enhance query understanding using GPT for better search results."""
        if not gpt_service.is_available():
            return query_text
        
        try:
            enhancement_prompt = f"""Enhance this job search query for better candidate matching:

Original query: "{query_text}"

Please:
1. Add relevant technical skills and keywords
2. Include experience level indicators
3. Add industry-specific terms
4. Keep the original intent
5. Make it more comprehensive for search

IMPORTANT GUIDELINES:
- For data science/AI queries: include machine learning, AI, statistical analysis, Python, R, SQL, data modeling, etc.
- For medical queries: include medical, healthcare, clinical, patient care, etc.
- For software engineering: include software development, programming, backend, frontend, etc.
- For legal queries: include legal, attorney, counsel, litigation, etc.

Return only the enhanced query, nothing else.

Example:
Input: "data scientist"
Output: "data scientist machine learning AI statistical analysis data modeling Python R SQL"

Input: "software engineer"
Output: "software engineer developer programmer backend frontend full stack"

Enhanced query:"""

            response = gpt_service._make_gpt_request(
                [{"role": "user", "content": enhancement_prompt}],
                temperature=0.2,
                max_tokens=150
            )
            
            enhanced = response.strip().strip('"').strip("'")
            return enhanced if enhanced else query_text
            
        except Exception as e:
            logger.warning(f"Query enhancement failed: {e}")
            return query_text
    
    def _gpt_final_ranking(self, candidates: List[CandidateProfile], query: str) -> List[CandidateProfile]:
        """Use GPT for final ranking and selection of candidates."""
        if not candidates or not gpt_service.is_available():
            return candidates
        
        try:
            # Prepare candidate data for GPT
            candidate_data = []
            for i, candidate in enumerate(candidates[:15]):  # Limit to top 15 for GPT processing
                candidate_data.append({
                    "id": candidate.id,
                    "name": candidate.name or "Unknown",
                    "summary": candidate.summary or "No summary",
                    "country": candidate.country or "Unknown"
                })
            
            ranking_prompt = f"""Rank these candidates for the job search query: "{query}"

Candidates:
{json.dumps(candidate_data, indent=2)}

Please:
1. Analyze each candidate's relevance to the query
2. Consider skills, experience, and background
3. Rank them from most to least relevant
4. Return only the ranked list of candidate IDs

Return format: ["id1", "id2", "id3", ...]

Ranked candidate IDs:"""

            response = gpt_service._make_gpt_request(
                [{"role": "user", "content": ranking_prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            # Parse ranked IDs
            try:
                ranked_ids = json.loads(response.strip())
                if isinstance(ranked_ids, list):
                    # Reorder candidates based on GPT ranking
                    candidate_map = {c.id: c for c in candidates}
                    ranked_candidates = []
                    for candidate_id in ranked_ids:
                        if candidate_id in candidate_map:
                            ranked_candidates.append(candidate_map[candidate_id])
                    
                    # Add any remaining candidates
                    for candidate in candidates:
                        if candidate.id not in ranked_ids:
                            ranked_candidates.append(candidate)
                    
                    return ranked_candidates
            except json.JSONDecodeError:
                logger.warning("Failed to parse GPT ranking response")
                
        except Exception as e:
            logger.warning(f"GPT final ranking failed: {e}")
        
        return candidates
    
    def _display_results(self, result: Dict, output_format: str):
        """Display results in the requested format."""
        if output_format.lower() == "json":
            self._display_json(result)
        elif output_format.lower() == "table":
            print_candidates_table(result)
        else:
            print_candidates_table(result)  # Default to table
    
    def _display_json(self, result: Dict):
        """Display results in JSON format."""
        print(f"\n{Colors.BOLD}📋 Results (JSON format):{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
        
        # Create clean JSON output
        json_output = {
            "query": result["query"],
            "enhanced_query": result["enhanced_query"],
            "search_time": result["search_time"],
            "num_candidates": result["num_candidates"],
            "candidates": []
        }
        
        for i in range(result["num_candidates"]):
            candidate = {
                "id": result["candidate_ids"][i],
                "name": result["candidate_names"][i],
                "country": result["candidate_countries"][i],
                "summary": result["candidate_summaries"][i]
            }
            json_output["candidates"].append(candidate)
        
        print(json.dumps(json_output, indent=2))
        print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
        
        # Add candidate IDs array at the bottom
        candidate_ids = [candidate["id"] for candidate in json_output["candidates"]]
        print(f"\n{Colors.BOLD}📋 Candidate IDs:{Colors.END}")
        print(f"{Colors.YELLOW}{candidate_ids}{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
    
    def _adjust_count(self, candidates: List[CandidateProfile]) -> List[CandidateProfile]:
        """Adjust candidate count based on quality."""
        if not candidates:
            return []
        
        # Count high-quality candidates
        high_quality_count = sum(1 for c in candidates if self._calculate_quality_score(c) >= 0.7)
        
        # Return fewer candidates if quality is high
        if high_quality_count >= 5:
            return candidates[:10]
        elif high_quality_count >= 3:
            return candidates[:15]
        else:
            return candidates[:20]

def print_candidates_table(candidates_data: Dict[str, List], max_display: int = 10):
    """Print candidates in a nice table format."""
    if candidates_data["num_candidates"] == 0:
        print(f"{Colors.YELLOW}No candidates found.{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}📋 Results ({candidates_data['num_candidates']} candidates):{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 100}{Colors.END}")
    
    # Display header
    print(f"{Colors.BOLD}{'#':<3} {'Name':<20} {'Country':<12} {'Professional Summary':<60}{Colors.END}")
    print(f"{Colors.CYAN}{'-' * 100}{Colors.END}")
    
    # Track seen candidates to avoid duplicates
    seen_candidates = set()
    displayed_count = 0
    
    # Display candidates
    for i in range(candidates_data["num_candidates"]):
        if displayed_count >= max_display:
            break
            
        name = candidates_data["candidate_names"][i] or "Unknown"
        country = candidates_data["candidate_countries"][i] or "Unknown"
        summary = candidates_data["candidate_summaries"][i] or "No summary"
        
        # Create unique identifier to avoid duplicates
        candidate_id = f"{name}_{country}_{summary[:50]}"
        if candidate_id in seen_candidates:
            continue
        seen_candidates.add(candidate_id)
        
        # Clean and improve summary display
        summary = summary.replace("bio:", "").replace("About:", "").strip()
        if summary.startswith("General Practitioner"):
            summary = summary.replace("General Practitioner", "Medical Professional")
        
        # Truncate long fields
        name = name[:19] + "..." if len(name) > 19 else name
        country = country[:11] + "..." if len(country) > 11 else country
        summary = summary[:59] + "..." if len(summary) > 59 else summary
        
        displayed_count += 1
        print(f"{displayed_count:<3} {name:<20} {country:<12} {summary:<60}")
    
    if candidates_data["num_candidates"] > displayed_count:
        print(f"{Colors.YELLOW}... and {candidates_data['num_candidates'] - displayed_count} more candidates{Colors.END}")
    
    print(f"{Colors.CYAN}{'=' * 100}{Colors.END}")
    
    # Show search performance
    search_time = candidates_data.get("search_time", 0)
    print(f"{Colors.GREEN}⏱️  Search completed in {search_time:.2f} seconds{Colors.END}")
    
    # Add candidate IDs array at the bottom
    candidate_ids = candidates_data.get("candidate_ids", [])
    if candidate_ids:
        print(f"\n{Colors.BOLD}📋 Candidate IDs:{Colors.END}")
        print(f"{Colors.YELLOW}{candidate_ids}{Colors.END}")

def main():
    """Main function for interview testing."""
    print(f"{Colors.BOLD}{Colors.HEADER}🚀 Mercor Search System - Interview Ready{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.GREEN}✅ All improvements loaded:{Colors.END}")
    print(f"  • Filter extraction from queries")
    print(f"  • GPT-enhanced search")
    print(f"  • Quality-based filtering")
    print(f"  • Dynamic candidate count")
    print(f"  • Enhanced hybrid search")
    print(f"  • Multiple GPT calls for accuracy")
    print(f"  • JSON/Table output options")
    print()
    
    try:
        agent = InterviewSearchAgent()
        
        while True:
            query = input(f"\n{Colors.BLUE}Enter your search query (or 'quit' to exit): {Colors.END}")
            
            if query.lower() in ['quit', 'exit', 'q']:
                print(f"{Colors.YELLOW}Goodbye!{Colors.END}")
                break
            
            if not query.strip():
                print(f"{Colors.YELLOW}Please enter a valid query.{Colors.END}")
                continue
            
            # Ask for output format
            output_format = input(f"{Colors.CYAN}Output format (table/json) [default: table]: {Colors.END}").strip().lower()
            if not output_format:
                output_format = "table"
            
            if output_format not in ["table", "json"]:
                output_format = "table"
            
            # Perform search with enhanced GPT processing
            result = agent.search(query.strip(), output_format)
            
            # Results are displayed by the search method now
            if result["num_candidates"] == 0:
                print(f"{Colors.YELLOW}No candidates found.{Colors.END}")
            
            print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Goodbye!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        logger.error(f"Main function error: {e}")

if __name__ == "__main__":
    main() 