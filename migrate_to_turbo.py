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

# --- Hardcoded API Keys ---
VOYAGE_API_KEY = "pa-vNEmoJfc5evP_SSvpxIAj3uFzs9dfppEZkpx-3kOFZy"
TURBOPUFFER_API_KEY = "tpuf_dQHBpZEvl612XAdP0MvrQY5dbS0omPMy"
OPENAI_API_KEY = "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"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_BATCH_SIZE = 10000
DEFAULT_NUM_THREADS = 10
MAX_RETRIES = 10
TURBOPUFFER_REGION = "aws-us-west-2"
COLLECTION_NAME = "linkedin_data_subset"
DB_NAME = "interview_data"
MONGO_URL = "os.getenv("MONGO_URL")"
TPUF_NAMESPACE_NAME = "bhaumik_tandan_tpuf_key"

# Init Turbopuffer
tpuf = turbopuffer.Turbopuffer(api_key=TURBOPUFFER_API_KEY, region=TURBOPUFFER_REGION)
ns = tpuf.namespace(TPUF_NAMESPACE_NAME)

def get_mongo_collection():
    client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
    return client[DB_NAME][COLLECTION_NAME]

def fetch_and_upsert_batch(skip: int, limit: int):
    collection = get_mongo_collection()
    logger.info(f"Fetching batch: skip={skip}, limit={limit}")

    cursor = (
        collection.find({}, {"embedding": 1, "email": 1, "rerankSummary": 1, "country": 1, "name": 1, "linkedinId": 1})
        .sort("_id", 1)
        .skip(skip)
        .limit(limit)
    )

    batch = []
    for doc in cursor:
        embedding = doc.get("embedding")
        if not embedding or not isinstance(embedding, list):
            continue

        profile = {
            "id": str(doc.get("_id")),
            "vector": embedding,
            "email": doc.get("email", ""),
            "rerank_summary": str(doc.get("rerankSummary", "") or ""),
            "country": doc.get("country", ""),
            "name": doc.get("name", ""),
            "linkedin_id": doc.get("linkedinId", ""),
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
                    "rerank_summary": {"type": "string", "full_text_search": True},
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
    parser = argparse.ArgumentParser(description="MongoDB to Turbopuffer migration tool")
    parser.add_argument("action", choices=["delete", "migrate"], default="migrate", nargs="?")
    parser.add_argument("--batch_size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--threads", type=int, default=DEFAULT_NUM_THREADS)
    args = parser.parse_args()

    if args.action == "delete":
        logger.info("Clearing Turbopuffer namespace...")
        delete_namespace()
        exit()

    logger.info("Starting migration from MongoDB to Turbopuffer")

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

    logger.info(f"Migration completed! Total processed: {total_processed}")
