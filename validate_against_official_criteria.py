"""
Official Mercor Criteria Validation
==================================
Validates final submission against official criteria from Mercor evaluation spreadsheet.
"""
import os
import sys
import json
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.utils.logger import setup_logger
logger = setup_logger("criteria_validator", level="INFO")
load_dotenv()
class OfficialCriteriaValidator:
    """Validates candidates against official Mercor criteria from the evaluation spreadsheet."""
    def __init__(self):
        self.mongo_url = os.getenv('MONGO_URL')
        self.db_name = "interview_data"
        self.collection_name = "linkedin_data_subset"
        self.official_criteria = {
            "tax_lawyer.yml": {
                "hard_criteria": [
                    "JD degree from an accredited U.S. law school",
                    "3+ years of experience practicing law"
                ],
                "soft_criteria": [
                    "Experience advising clients on tax implications of corporate or financial transactions",
                    "Experience handling IRS audits, disputes, or regulatory inquiries", 
                    "Experience drafting legal opinions or filings related to federal and state tax compliance"
                ],
                "keywords_required": ["JD", "attorney", "lawyer", "legal", "law school"],
                "keywords_preferred": ["tax", "IRS", "audit", "corporate tax", "federal tax", "tax compliance", "tax structuring"],
                "keywords_exclude": ["paralegal", "intern", "student"]
            },
            "junior_corporate_lawyer.yml": {
                "hard_criteria": [
                    "2-4 years of experience as a Corporate Lawyer at a leading law firm in the USA, Europe, or Canada",
                    "Graduate of a reputed law school in the USA, Europe, or Canada"
                ],
                "soft_criteria": [
                    "Experience supporting Corporate M&A transactions, including due diligence and legal documentation",
                    "Experience drafting and negotiating legal contracts or commercial agreements",
                    "Familiarity with international business law or advising on regulatory requirements across jurisdictions"
                ],
                "keywords_required": ["JD", "attorney", "lawyer", "legal", "corporate", "law school"],
                "keywords_preferred": ["M&A", "mergers", "acquisitions", "contracts", "due diligence", "international law"],
                "keywords_exclude": ["paralegal", "intern", "student"]
            },
            "radiology.yml": {
                "hard_criteria": [
                    "MD degree from a medical school in the U.S. or India"
                ],
                "soft_criteria": [
                    "Board certification in Radiology (ABR, FRCR, or equivalent) or comparable credential",
                    "3+ years of experience interpreting X-ray, CT, MRI, ultrasound, or nuclear medicine studies",
                    "Expertise in radiology reporting, diagnostic protocols, differential diagnosis, or AI applications in medical imaging"
                ],
                "keywords_required": ["MD", "doctor", "physician", "medical", "radiology"],
                "keywords_preferred": ["radiologist", "CT", "MRI", "X-ray", "ultrasound", "DICOM", "imaging", "diagnostic"],
                "keywords_exclude": ["nurse", "technician", "student"]
            },
            "doctors_md.yml": {
                "hard_criteria": [
                    "MD degree from a top U.S. medical school",
                    "2+ years of clinical practice experience in the U.S.",
                    "Experience working as a General Practitioner (GP)"
                ],
                "soft_criteria": [
                    "Familiarity with EHR systems and managing high patient volumes in outpatient or family medicine settings",
                    "Comfort with telemedicine consultations, patient triage, and interdisciplinary coordination"
                ],
                "keywords_required": ["MD", "doctor", "physician", "medical", "clinical", "practice"],
                "keywords_preferred": ["GP", "general practitioner", "primary care", "family medicine", "EHR", "telemedicine"],
                "keywords_exclude": ["nurse", "technician", "student"]
            },
            "biology_expert.yml": {
                "hard_criteria": [
                    "Completed undergraduate studies in the U.S., U.K., or Canada",
                    "PhD in Biology from a top U.S. university"
                ],
                "soft_criteria": [
                    "Research experience in molecular biology, genetics, or cell biology, with publications in peer-reviewed journals",
                    "Familiarity with experimental design, data analysis, and lab techniques such as CRISPR, PCR, or sequencing",
                    "Experience mentoring students, teaching undergraduate biology courses, or collaborating on interdisciplinary research"
                ],
                "keywords_required": ["PhD", "biology", "research", "university"],
                "keywords_preferred": ["molecular biology", "genetics", "cell biology", "CRISPR", "PCR", "sequencing", "publications"],
                "keywords_exclude": ["undergraduate", "bachelor", "student"]
            },
            "anthropology.yml": {
                "hard_criteria": [
                    "PhD (in progress or completed) from a distinguished program in sociology, anthropology, or economics",
                    "PhD program started within the last 3 years"
                ],
                "soft_criteria": [
                    "Demonstrated expertise in ethnographic methods, with substantial fieldwork or case study research",
                    "Strong academic output — published papers, working papers, or conference presentations on anthropological or sociological topics",
                    "Experience applying anthropological theory to real-world or interdisciplinary contexts"
                ],
                "keywords_required": ["PhD", "anthropology", "sociology", "research"],
                "keywords_preferred": ["ethnographic", "fieldwork", "cultural", "social", "migration", "labor", "publications"],
                "keywords_exclude": ["undergraduate", "bachelor", "student"]
            },
            "mathematics_phd.yml": {
                "hard_criteria": [
                    "Completed undergraduate studies in the U.S., U.K., or Canada",
                    "PhD in Mathematics or Statistics from a top U.S. university"
                ],
                "soft_criteria": [
                    "Research expertise in pure or applied mathematics, statistics, or probability, with peer-reviewed publications or preprints",
                    "Proficiency in mathematical modeling, proof-based reasoning, or algorithmic problem-solving"
                ],
                "keywords_required": ["PhD", "mathematics", "statistics", "research", "university"],
                "keywords_preferred": ["mathematical modeling", "probability", "statistics", "algorithms", "publications", "pure mathematics"],
                "keywords_exclude": ["undergraduate", "bachelor", "student"]
            },
            "quantitative_finance.yml": {
                "hard_criteria": [
                    "MBA from a Prestigious U.S. university (M7 MBA)",
                    "3+ years of experience in quantitative finance, including roles such as risk modeling, algorithmic trading, or financial engineering"
                ],
                "soft_criteria": [
                    "Experience applying financial modeling techniques to real-world problems like portfolio optimization or derivatives pricing",
                    "Proficiency with Python for quantitative analysis and exposure to financial libraries",
                    "Demonstrated ability to work in high-stakes environments such as global investment firms"
                ],
                "keywords_required": ["MBA", "finance", "quantitative", "financial"],
                "keywords_preferred": ["risk modeling", "algorithmic trading", "Python", "portfolio optimization", "derivatives", "investment"],
                "keywords_exclude": ["undergraduate", "bachelor", "student"]
            },
            "bankers.yml": {
                "hard_criteria": [
                    "MBA from a U.S. university",
                    "2+ years of prior work experience in investment banking, corporate finance, or M&A advisory"
                ],
                "soft_criteria": [
                    "Specialized experience in healthcare-focused investment banking or private equity",
                    "Led or contributed to transactions involving healthcare M&A, recapitalizations, or growth equity investments",
                    "Familiarity with healthcare-specific metrics, regulatory frameworks, and value creation strategies"
                ],
                "keywords_required": ["MBA", "banking", "investment", "finance"],
                "keywords_preferred": ["investment banking", "M&A", "healthcare", "private equity", "transactions"],
                "keywords_exclude": ["undergraduate", "bachelor", "student"]
            },
            "mechanical_engineers.yml": {
                "hard_criteria": [
                    "Higher degree in Mechanical Engineering from an accredited university",
                    "3+ years of professional experience in mechanical design, product development, or systems engineering"
                ],
                "soft_criteria": [
                    "Experience with CAD tools (e.g., SolidWorks, AutoCAD) and mechanical simulation tools (e.g., ANSYS, COMSOL)",
                    "Demonstrated involvement in end-to-end product lifecycle — from concept through prototyping to manufacturing or testing",
                    "Domain specialization in areas like thermal systems, fluid dynamics, structural analysis, or mechatronics"
                ],
                "keywords_required": ["engineering", "mechanical", "design", "development"],
                "keywords_preferred": ["CAD", "SolidWorks", "AutoCAD", "ANSYS", "COMSOL", "thermal", "fluid dynamics", "mechatronics"],
                "keywords_exclude": ["undergraduate", "bachelor", "student"]
            }
        }
        logger.info("Official Criteria Validator initialized with Mercor spreadsheet criteria")
    def get_mongo_collection(self):
        """Get MongoDB collection."""
        if not self.mongo_url:
            logger.warning("MongoDB URL not configured")
            return None
        try:
            client = MongoClient(self.mongo_url, tlsCAFile=certifi.where())
            return client[self.db_name][self.collection_name]
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return None
    def get_candidate_data(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get candidate data from MongoDB."""
        collection = self.get_mongo_collection()
        if collection is None:
            return None
        try:
            from bson import ObjectId
            try:
                mongo_id = ObjectId(candidate_id)
            except:
                mongo_id = candidate_id
            mongo_doc = collection.find_one({"_id": mongo_id})
            if not mongo_doc:
                return None
            return {
                "id": str(mongo_doc.get("_id", "")),
                "name": mongo_doc.get("name", ""),
                "email": mongo_doc.get("email", ""),
                "summary": mongo_doc.get("rerankSummary", ""),
                "linkedin_id": mongo_doc.get("linkedinId", ""),
                "country": mongo_doc.get("country", ""),
                "experience": mongo_doc.get("experience", ""),
                "education": mongo_doc.get("education", ""),
                "position": mongo_doc.get("position", ""),
                "company": mongo_doc.get("company", ""),
                "raw_data": mongo_doc
            }
        except Exception as e:
            logger.error(f"Failed to get candidate data for {candidate_id}: {e}")
            return None
    def validate_candidate_against_criteria(self, candidate_data: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Validate a single candidate against official criteria."""
        if category not in self.official_criteria:
            return {"error": f"No criteria defined for {category}"}
        criteria = self.official_criteria[category]
        def safe_text(field):
            value = candidate_data.get(field, "")
            if isinstance(value, list):
                return " ".join(str(item) for item in value if item)
            return str(value) if value else ""
        all_text = " ".join([
            safe_text("name"),
            safe_text("summary"),
            safe_text("experience"),
            safe_text("education"),
            safe_text("position"),
            safe_text("company")
        ]).lower()
        validation_result = {
            "candidate_id": candidate_data["id"],
            "candidate_name": candidate_data.get("name", "Unknown"),
            "category": category,
            "hard_criteria_score": 0.0,
            "soft_criteria_score": 0.0,
            "overall_compliance": 0.0,
            "required_keywords_found": [],
            "preferred_keywords_found": [],
            "excluded_keywords_found": [],
            "hard_criteria_details": [],
            "soft_criteria_details": [],
            "recommendations": []
        }
        required_keywords = criteria["keywords_required"]
        found_required = []
        for keyword in required_keywords:
            if keyword.lower() in all_text:
                found_required.append(keyword)
        validation_result["required_keywords_found"] = found_required
        validation_result["hard_criteria_score"] = len(found_required) / len(required_keywords) if required_keywords else 0.0
        preferred_keywords = criteria["keywords_preferred"]
        found_preferred = []
        for keyword in preferred_keywords:
            if keyword.lower() in all_text:
                found_preferred.append(keyword)
        validation_result["preferred_keywords_found"] = found_preferred
        validation_result["soft_criteria_score"] = len(found_preferred) / len(preferred_keywords) if preferred_keywords else 0.0
        excluded_keywords = criteria["keywords_exclude"]
        found_excluded = []
        for keyword in excluded_keywords:
            if keyword.lower() in all_text:
                found_excluded.append(keyword)
        validation_result["excluded_keywords_found"] = found_excluded
        hard_weight = 0.7
        soft_weight = 0.3
        exclusion_penalty = 0.2 * len(found_excluded)
        validation_result["overall_compliance"] = max(0.0, 
            (hard_weight * validation_result["hard_criteria_score"] + 
             soft_weight * validation_result["soft_criteria_score"]) - exclusion_penalty
        )
        if validation_result["hard_criteria_score"] < 0.6:
            validation_result["recommendations"].append("Missing key required qualifications")
        if validation_result["soft_criteria_score"] < 0.3:
            validation_result["recommendations"].append("Limited relevant experience indicators")
        if found_excluded:
            validation_result["recommendations"].append(f"Contains exclusion keywords: {', '.join(found_excluded)}")
        return validation_result
    def validate_submission(self, submission_file: str) -> Dict[str, Any]:
        """Validate entire submission against official criteria."""
        logger.info(f"Validating submission file: {submission_file}")
        try:
            with open(submission_file, 'r') as f:
                submission = json.load(f)
        except Exception as e:
            return {"error": f"Failed to load submission: {e}"}
        config_candidates = submission.get("config_candidates", {})
        validation_results = {
            "submission_file": submission_file,
            "total_categories": len(config_candidates),
            "total_candidates": sum(len(ids) for ids in config_candidates.values()),
            "category_results": {},
            "overall_compliance": 0.0,
            "categories_passing": 0,
            "categories_failing": 0,
            "summary": {}
        }
        category_scores = []
        for category, candidate_ids in config_candidates.items():
            logger.info(f"Validating category: {category}")
            category_result = {
                "category": category,
                "candidate_count": len(candidate_ids),
                "candidates": [],
                "average_compliance": 0.0,
                "passing_candidates": 0,
                "failing_candidates": 0
            }
            candidate_scores = []
            for i, candidate_id in enumerate(candidate_ids):
                logger.info(f"  Validating candidate {i+1}/{len(candidate_ids)}: {candidate_id}")
                candidate_data = self.get_candidate_data(candidate_id)
                if not candidate_data:
                    logger.warning(f"    No data found for candidate {candidate_id}")
                    continue
                candidate_validation = self.validate_candidate_against_criteria(candidate_data, category)
                category_result["candidates"].append(candidate_validation)
                compliance_score = candidate_validation["overall_compliance"]
                candidate_scores.append(compliance_score)
                if compliance_score >= 0.6:  # 60% compliance threshold
                    category_result["passing_candidates"] += 1
                else:
                    category_result["failing_candidates"] += 1
                logger.info(f"    Compliance: {compliance_score:.3f}")
            if candidate_scores:
                category_result["average_compliance"] = sum(candidate_scores) / len(candidate_scores)
                category_scores.append(category_result["average_compliance"])
            validation_results["category_results"][category] = category_result
            if category_result["average_compliance"] >= 0.6:
                validation_results["categories_passing"] += 1
            else:
                validation_results["categories_failing"] += 1
        if category_scores:
            validation_results["overall_compliance"] = sum(category_scores) / len(category_scores)
        validation_results["summary"] = {
            "overall_grade": self._get_grade(validation_results["overall_compliance"]),
            "categories_passing_rate": validation_results["categories_passing"] / validation_results["total_categories"] if validation_results["total_categories"] > 0 else 0.0,
            "top_performing_categories": sorted(
                [(cat, result["average_compliance"]) for cat, result in validation_results["category_results"].items()],
                key=lambda x: x[1], reverse=True
            )[:3],
            "needs_improvement_categories": sorted(
                [(cat, result["average_compliance"]) for cat, result in validation_results["category_results"].items()],
                key=lambda x: x[1]
            )[:3]
        }
        return validation_results
    def _get_grade(self, score: float) -> str:
        """Get letter grade for compliance score."""
        if score >= 0.9:
            return "A (Excellent)"
        elif score >= 0.8:
            return "B (Good)"
        elif score >= 0.7:
            return "C (Satisfactory)"
        elif score >= 0.6:
            return "D (Needs Improvement)"
        else:
            return "F (Failing)"
    def generate_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a detailed validation report."""
        report = []
        report.append("=" * 80)
        report.append("OFFICIAL MERCOR CRITERIA VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        summary = validation_results["summary"]
        report.append(f"📊 OVERALL RESULTS:")
        report.append(f"   Total Categories: {validation_results['total_categories']}")
        report.append(f"   Total Candidates: {validation_results['total_candidates']}")
        report.append(f"   Overall Compliance: {validation_results['overall_compliance']:.3f}")
        report.append(f"   Overall Grade: {summary['overall_grade']}")
        report.append(f"   Categories Passing: {validation_results['categories_passing']}/{validation_results['total_categories']}")
        report.append("")
        report.append("🏆 TOP PERFORMING CATEGORIES:")
        for category, score in summary["top_performing_categories"]:
            report.append(f"   {category}: {score:.3f}")
        report.append("")
        report.append("⚠️  NEEDS IMPROVEMENT:")
        for category, score in summary["needs_improvement_categories"]:
            report.append(f"   {category}: {score:.3f}")
        report.append("")
        report.append("📋 DETAILED CATEGORY ANALYSIS:")
        report.append("")
        for category, result in validation_results["category_results"].items():
            report.append(f"Category: {category}")
            report.append(f"  Average Compliance: {result['average_compliance']:.3f}")
            report.append(f"  Passing Candidates: {result['passing_candidates']}/{result['candidate_count']}")
            top_candidates = sorted(result["candidates"], 
                                   key=lambda x: x["overall_compliance"], reverse=True)[:3]
            report.append("  Top Candidates:")
            for candidate in top_candidates:
                report.append(f"    {candidate['candidate_name']}: {candidate['overall_compliance']:.3f}")
                if candidate['required_keywords_found']:
                    report.append(f"      Required: {', '.join(candidate['required_keywords_found'])}")
                if candidate['preferred_keywords_found']:
                    report.append(f"      Preferred: {', '.join(candidate['preferred_keywords_found'])}")
            report.append("")
        return "\n".join(report)
def main():
    """Main validation function."""
    print("🔍 VALIDATING SUBMISSION AGAINST OFFICIAL MERCOR CRITERIA")
    print("=" * 60)
    validator = OfficialCriteriaValidator()
    if os.path.exists("final_submission.json"):
        results = validator.validate_submission("final_submission.json")
        if "error" in results:
            print(f"❌ Validation failed: {results['error']}")
            return
        report = validator.generate_report(results)
        print(report)
        with open("official_criteria_validation_report.json", "w") as f:
            json.dump(results, f, indent=2)
        print("📄 Detailed validation saved to: official_criteria_validation_report.json")
        overall_score = results["overall_compliance"]
        if overall_score >= 0.8:
            print("🎉 EXCELLENT: Submission meets high standards!")
        elif overall_score >= 0.6:
            print("✅ GOOD: Submission meets acceptable standards")
        else:
            print("⚠️  NEEDS IMPROVEMENT: Consider refining candidate selection")
    else:
        print("❌ No final_submission.json found. Please run the submission agent first.")
if __name__ == "__main__":
    main() 