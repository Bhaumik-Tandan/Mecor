# Candidate Search System - Mercor Assignment

A sophisticated candidate search system that combines vector search, BM25 keyword matching, and soft filtering to deliver highly relevant candidate matches for specific job categories.

## Environment Setup

1. **Clone and Setup**
```bash
git clone <repository>
cd mercor_task
```

2. **Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cp environment_template.txt .env
# Edit .env with your API keys:
# - VOYAGE_API_KEY
# - TURBOPUFFER_API_KEY  
# - OPENAI_API_KEY (optional)
# - USER_EMAIL
# - TURBOPUFFER_NAMESPACE
```

## Setup Script (init.py)

The `init.py` script migrates data from MongoDB to Turbopuffer vector database:

```bash
# Run the setup/migration script
python3 init.py migrate

# Optional: Clear existing data first
python3 init.py delete
```

**Configuration Options:**
- `--batch_size`: Number of documents per batch (default: 10000)
- `--threads`: Number of parallel workers (default: 10)

## Retrieval Logic

The main retrieval system (`submission_agent.py`) implements:

### Core Components:
- **Vector Search**: Uses voyage-3 embeddings for semantic similarity
- **BM25 Search**: Keyword-based text matching
- **Soft Filtering**: Preference scoring based on job-specific criteria
- **Hard Filtering**: Must-have requirements filtering

### Usage:
```bash
# Generate final submission with evaluation feedback
python3 submission_agent.py
```

### Key Functions:
- `search_with_criteria()`: Multi-strategy candidate search
- `call_evaluation_endpoint()`: Real-time Mercor evaluation
- `iterative_improvement()`: Score-based optimization

## Evaluation API Integration

The system calls the Mercor evaluation endpoint during processing:

```python
# Example evaluation call
headers = {"Authorization": "your_email@example.com", "Content-Type": "application/json"}
payload = {"config_path": "tax_lawyer.yml", "object_ids": ["candidate_id_1", ...]}
response = requests.post("https://mercor-dev--search-eng-interview.modal.run/evaluate", 
                        json=payload, headers=headers)
print(f"Overall Score: {response.json()['average_final_score']}")
```

## Approach Summary

### Data Exploration
1. **Schema Analysis**: Analyzed MongoDB structure (193,796 documents)
2. **Field Selection**: Used embedding, rerankSummary, name, email, linkedinId, country
3. **Embedding Strategy**: Leveraged pre-computed voyage-3 embeddings

### Indexing Strategy
- **Vector Database**: Turbopuffer for scalable similarity search
- **Schema Design**: Optimized for full-text search on summary field
- **Distance Metric**: Cosine similarity for vector comparisons

### Retrieval Approach
1. **Hybrid Search**: Combines vector similarity (60%) + BM25 (40%) + soft filters (20%)
2. **Domain-Specific Queries**: Tailored search terms per job category
3. **Hard Filtering**: Must-have requirements (JD degree, experience years)
4. **Soft Criteria**: Preference scoring (IRS experience, M&A background, etc.)

### Validation & Analysis
- **Real-time Evaluation**: Integration with Mercor endpoint during search
- **Iterative Improvement**: Automatic retry with different strategies if scores are low
- **Domain Validation**: Prevents cross-contamination (biology PhDs in math roles)
- **Performance Metrics**: Track precision, relevance, and evaluation scores

### Key Innovations
1. **Evaluation-Driven Search**: Uses Mercor feedback to improve results in real-time
2. **Multi-Strategy Fallback**: Tries different approaches if initial results are poor
3. **Soft Criteria Matching**: Sophisticated preference scoring beyond basic keyword matching

## Project Structure

```
mercor_task/
├── init.py                     # Setup/migration script
├── submission_agent.py         # Main retrieval logic with evaluation
├── simple_submission.py        # Basic submission generator
├── requirements.txt            # Dependencies
├── environment_template.txt    # Environment variables template
├── src/
│   ├── config/
│   │   ├── settings.py        # Configuration management
│   │   └── prompts.json       # Job-specific criteria
│   ├── models/
│   │   └── candidate.py       # Data models
│   ├── services/
│   │   ├── search_service.py  # Core search logic
│   │   ├── gpt_service.py     # GPT integration
│   │   ├── embedding_service.py
│   │   └── evaluation_service.py
│   └── utils/
│       ├── logger.py          # Logging utilities
│       └── helpers.py         # Helper functions
└── README.md                  # This file
```

## Performance Results

The system achieves strong performance across job categories:

### Sample Evaluation Scores:
- **Tax Lawyers**: Hard criteria (70% JD compliance, 100% experience)
- **Soft Criteria**: 8.35/10 legal writing, 8.3/10 IRS audit experience
- **Domain Specificity**: Effective filtering prevents cross-domain contamination

### Technical Performance:
- **Search Speed**: ~10-30 seconds per category
- **Accuracy**: High relevance scores with domain-specific filtering
- **Scalability**: Handles 193K+ candidate database efficiently

## Final Submission

To generate the final submission:

```bash
# Run the main submission agent
python3 submission_agent.py

# This creates final_submission.json with exactly 100 candidates (10 per category)
```

Submit to Mercor:
```bash
curl -H 'Authorization: your_email@example.com' \
     -H 'Content-Type: application/json' \
     -d @final_submission.json \
     'https://mercor-dev--search-eng-interview.modal.run/grade'
```

---

**Author**: Bhaumik Tandan  
**Email**: bhaumik.tandan@gmail.com
