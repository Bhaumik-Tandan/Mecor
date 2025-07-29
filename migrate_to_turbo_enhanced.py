import turbopuffer
import time
import concurrent.futures
from threading import Lock
import argparse
import logging
import os
import traceback
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Keys from Environment Variables ---
VOYAGE_API_KEY = os.getenv('VOYAGE_API_KEY')
TURBOPUFFER_API_KEY = os.getenv('TURBOPUFFER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_BATCH_SIZE = 10000
DEFAULT_NUM_THREADS = 10
MAX_RETRIES = 10
TURBOPUFFER_REGION = os.getenv('TURBOPUFFER_REGION', 'aws-us-west-2')
COLLECTION_NAME = "linkedin_data_subset"
DB_NAME = "interview_data"
MONGO_URL = os.getenv('MONGO_URL')
TPUF_NAMESPACE_NAME = os.getenv('TURBOPUFFER_NAMESPACE', 'bhaumik_tandan_tpuf_key')

# Validate required environment variables
if not TURBOPUFFER_API_KEY:
    raise ValueError("TURBOPUFFER_API_KEY environment variable is required")
if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is required")

# Init Turbopuffer
tpuf = turbopuffer.Turbopuffer(api_key=TURBOPUFFER_API_KEY, region=TURBOPUFFER_REGION)
ns = tpuf.namespace(TPUF_NAMESPACE_NAME)

def get_mongo_collection():
    client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
    return client[DB_NAME][COLLECTION_NAME]

def process_experience_data(experience_list):
    """Process experience list to create searchable text."""
    if not experience_list or not isinstance(experience_list, list):
        return ""
    
    experience_texts = []
    for exp in experience_list:
        if isinstance(exp, dict):
            # Extract relevant experience fields
            title = exp.get('title', exp.get('position', ''))
            company = exp.get('company', exp.get('organization', ''))
            description = exp.get('description', exp.get('summary', ''))
            
            exp_text = f"{title} at {company}. {description}".strip()
            if exp_text != " at .":  # Avoid empty entries
                experience_texts.append(exp_text)
    
    return " | ".join(experience_texts)

def process_skills_data(skills_list):
    """Process skills list to create searchable text."""
    if not skills_list or not isinstance(skills_list, list):
        return ""
    
    # Handle both string skills and dict skills
    skill_names = []
    for skill in skills_list:
        if isinstance(skill, str):
            skill_names.append(skill)
        elif isinstance(skill, dict):
            name = skill.get('name', skill.get('skill', ''))
            if name:
                skill_names.append(name)
    
    return ", ".join(skill_names)

def process_education_data(education_dict):
    """Process education data to create searchable text."""
    if not education_dict or not isinstance(education_dict, dict):
        return ""
    
    education_texts = []
    
    # Add highest level
    highest_level = education_dict.get('highest_level', '')
    if highest_level:
        education_texts.append(f"Education Level: {highest_level}")
    
    # Process degrees
    degrees = education_dict.get('degrees', [])
    if isinstance(degrees, list):
        for degree in degrees:
            if isinstance(degree, dict):
                degree_name = degree.get('degree', degree.get('name', ''))
                institution = degree.get('institution', degree.get('school', ''))
                field = degree.get('field', degree.get('major', ''))
                
                degree_text = f"{degree_name} in {field} from {institution}".strip()
                if degree_text not in ["in from", " in  from "]:  # Avoid empty entries
                    education_texts.append(degree_text)
    
    return " | ".join(education_texts)

def process_awards_certifications(awards_list):
    """Process awards and certifications to create searchable text."""
    if not awards_list or not isinstance(awards_list, list):
        return ""
    
    items = []
    for item in awards_list:
        if isinstance(item, str):
            items.append(item)
        elif isinstance(item, dict):
            name = item.get('name', item.get('title', ''))
            issuer = item.get('issuer', item.get('organization', ''))
            if name:
                if issuer:
                    items.append(f"{name} from {issuer}")
                else:
                    items.append(name)
    
    return ", ".join(items)

def fetch_and_upsert_batch(skip: int, limit: int):
    collection = get_mongo_collection()
    logger.info(f"Fetching batch: skip={skip}, limit={limit}")

    # Enhanced field selection for improved search
    cursor = (
        collection.find({}, {
            "embedding": 1, 
            "email": 1, 
            "rerankSummary": 1, 
            "country": 1, 
            "name": 1, 
            "linkedinId": 1,
            # Additional search-enhancing fields
            "headline": 1,
            "experience": 1,
            "skills": 1,
            "education": 1,
            "awardsAndCertifications": 1,
            "yearsOfWorkExperience": 1,
            "personId": 1,
            "prestigeScore": 1
        })
        .sort("_id", 1)
        .skip(skip)
        .limit(limit)
    )

    batch = []
    for doc in cursor:
        embedding = doc.get("embedding")
        if not embedding or not isinstance(embedding, list):
            continue

        # Process complex fields
        experience_text = process_experience_data(doc.get("experience", []))
        skills_text = process_skills_data(doc.get("skills", []))
        education_text = process_education_data(doc.get("education", {}))
        awards_text = process_awards_certifications(doc.get("awardsAndCertifications", []))
        
        # Create comprehensive searchable summary
        searchable_fields = [
            doc.get("rerankSummary", ""),
            doc.get("headline", ""),
            experience_text,
            skills_text,
            education_text,
            awards_text
        ]
        comprehensive_summary = " | ".join([field for field in searchable_fields if field])

        profile = {
            "id": str(doc.get("_id")),
            "vector": embedding,
            # Core fields
            "email": doc.get("email", ""),
            "rerank_summary": str(doc.get("rerankSummary", "") or ""),
            "country": doc.get("country", ""),
            "name": doc.get("name", ""),
            "linkedin_id": doc.get("linkedinId", ""),
            # Enhanced search fields
            "headline": str(doc.get("headline", "") or ""),
            "experience_text": experience_text,
            "skills_text": skills_text,
            "education_text": education_text,
            "awards_certifications": awards_text,
            "years_experience": doc.get("yearsOfWorkExperience", 0),
            "person_id": doc.get("personId", ""),
            "prestige_score": doc.get("prestigeScore", 0),
            # Comprehensive searchable field combining all text
            "comprehensive_summary": comprehensive_summary
        }
        batch.append(profile)

    if not batch:
        logger.info("No valid documents found in batch")
        return 0

    return len(batch) if upsert_batch_to_turbopuffer(batch) else 0

def upsert_batch_to_turbopuffer(batch):
    for i in range(MAX_RETRIES):
        try:
            ns.write(
                upsert_rows=batch,
                distance_metric="cosine_distance",
                schema={
                    "id": "string",
                    # Full-text searchable fields for BM25
                    "rerank_summary": {"type": "string", "full_text_search": True},
                    "headline": {"type": "string", "full_text_search": True},
                    "experience_text": {"type": "string", "full_text_search": True},
                    "skills_text": {"type": "string", "full_text_search": True},
                    "education_text": {"type": "string", "full_text_search": True},
                    "awards_certifications": {"type": "string", "full_text_search": True},
                    "comprehensive_summary": {"type": "string", "full_text_search": True},
                    # Metadata fields
                    "name": "string",
                    "email": "string",
                    "country": "string",
                    "linkedin_id": "string",
                    "person_id": "string",
                    "years_experience": "int64",
                    "prestige_score": "int64",
                },
            )
            logger.info(f"Successfully upserted batch of size {len(batch)}")
            return True
        except Exception as e:
            logger.error(f"Upsert error: {e}\n{traceback.format_exc()}")
            time.sleep(i + 1)
    return False

def get_total_document_count():
    return get_mongo_collection().count_documents({})

def delete_namespace():
    try:
        ns.delete_all()
        logger.info("Namespace cleared successfully")
    except Exception as e:
        logger.error(f"Namespace clear error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced MongoDB to Turbopuffer migration tool")
    parser.add_argument("action", choices=["delete", "migrate"], default="migrate", nargs="?")
    parser.add_argument("--batch_size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--threads", type=int, default=DEFAULT_NUM_THREADS)
    args = parser.parse_args()

    if args.action == "delete":
        logger.info("Clearing Turbopuffer namespace...")
        delete_namespace()
        exit()

    logger.info("Starting ENHANCED migration from MongoDB to Turbopuffer")
    logger.info("🚀 Additional search fields: headline, experience, skills, education, awards")

    total_docs = get_total_document_count()
    logger.info(f"Total documents: {total_docs}")

    batch_ranges = [(skip, args.batch_size) for skip in range(0, total_docs, args.batch_size)]
    total_processed = 0
    lock = Lock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(fetch_and_upsert_batch, skip, limit) for skip, limit in batch_ranges]
        for future in concurrent.futures.as_completed(futures):
            try:
                batch_count = future.result()
            except Exception as e:
                logger.error(f"Batch failed: {e}\n{traceback.format_exc()}")
                batch_count = 0

            with lock:
                total_processed += batch_count
            logger.info(f"Processed so far: {total_processed}")

    logger.info(f"🎉 Enhanced migration completed! Total processed: {total_processed}")
    logger.info("✅ Now supports search on: headlines, experience, skills, education, certifications") 