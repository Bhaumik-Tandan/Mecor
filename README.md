# MCP-Enhanced Candidate Search System

Fast, parallel candidate search with GPT enhancement and MCP (Model Context Protocol) support.

## Environment Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd mercor_task

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running Setup Script
```bash
# Initialize system (first time)
python3 init.py

# Rebuild embeddings index (if needed)
python3 init.py --rebuild-index

# Verify setup only
python3 init.py --verify-only
```

## Usage

### Main Retrieval System
```bash
# Run the main search system
python3 main.py
```

### Evaluation Example
```python
import requests
import json

# Load candidates from submission
with open("final_submission.json", "r") as f:
    submission = json.load(f)

# Evaluate a category
category = "biology_expert.yml"
candidate_ids = submission["config_candidates"][category]

response = requests.post(
    "https://mercor-dev--search-eng-interview.modal.run/evaluate",
    headers={
        "Authorization": "bhaumik.tandan@gmail.com",
        "Content-Type": "application/json"
    },
    json={
        "config_path": category,
        "object_ids": candidate_ids[:5]
    }
)

if response.status_code == 200:
    score = response.json().get('overallScore', 0)
    print(f"Overall Score for {category}: {score}")
```

## Results - Public Query Scores

| Category | Score | Candidates |
|----------|--------|------------|
| tax_lawyer.yml | 69.333 | 10 |
| junior_corporate_lawyer.yml | 48.000 | 10 |
| radiology.yml | 0.000 | 10 |
| doctors_md.yml | 13.000 | 10 |
| biology_expert.yml | 18.000 | 10 |
| anthropology.yml | 80.000 | 10 |
| mathematics_phd.yml | 15.000 | 10 |
| quantitative_finance.yml | 0.000 | 10 |
| bankers.yml | 33.333 | 10 |
| mechanical_engineers.yml | 68.667 | 10 |

**Average Score**: 34.533

## Approach Summary

### Data Exploration & Strategy Selection
1. **Evaluation Criteria Analysis**: Used official [evaluation spreadsheet](https://docs.google.com/spreadsheets/d/1BggMRCZ0BBRhrhOJWAQqE_3FPO85E7fMVKF3I1d_S0Q/edit?gid=0#gid=0) to identify:
   - **Hard Criteria**: Must-have requirements (JD, MD, PhD degrees, experience years)
   - **Soft Criteria**: Preferred qualifications (specializations, tools, certifications)
   - **Score Improvement**: 3x better results by targeting exact criteria

2. **Strategy Analysis**: 
   - Criteria-based search queries proved most effective
   - Targeted hard requirements essential for non-zero scores
   - Specific experience years and credentials critical for evaluation

### Indexing & Retrieval Strategy
- **Embedding Service**: Uses OpenAI embeddings for semantic search
- **Search Strategies**: Vector-only (primary), BM25, Hybrid available
- **MCP Integration**: Context-aware query enhancement with caching
- **Query Enhancement**: GPT-4 optimizes search terms per category

### Validation & Analysis
- **Performance Testing**: Benchmarked all strategies for efficiency
- **Quality Metrics**: MCP scoring for soft criteria evaluation
- **Caching**: Prevents redundant GPT calls for identical queries
- **Parallel Processing**: ThreadPoolExecutor for concurrent category processing

### Architecture
```
MCPFastAgent
├── mcp_enhance_query()     # GPT-enhanced search terms with caching
├── mcp_search_with_context() # Vector search with MCP context
├── mcp_evaluate_soft_criteria() # API evaluation with scoring
└── mcp_process_category()  # Full MCP workflow per category
```

## Key Features

- 🚀 **Parallel Processing**: 4 concurrent workers
- 🤖 **MCP Enhancement**: Context-aware query optimization
- ⚡ **Efficient Search**: Vector-only strategy (0.86 candidates/sec)
- 📊 **Smart Caching**: Avoids duplicate GPT calls
- 🎯 **Quality Scoring**: Soft criteria evaluation
- 📈 **Analytics**: Detailed performance tracking

## Files Structure

- `main.py` - Main retrieval logic with MCP support
- `init.py` - Setup script for environment and embeddings
- `final_submission.json` - Standard submission format
- `mcp_analysis.json` - Detailed MCP context and performance data
- `src/` - Core services and models
  - `services/` - Search, GPT, and embedding services
  - `models/` - Candidate and query models
  - `config/` - Configuration and settings

## Configuration Options

The system supports various flags and configurations:

- `--rebuild-index`: Rebuild embeddings from scratch
- `--verify-only`: Test setup without full initialization
- Vector strategy selection via `SearchStrategy` enum
- Parallel worker count adjustment in `ThreadPoolExecutor`
- GPT model and token limits in `GPTService` 