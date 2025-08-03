# Mercor Search Engineering Challenge - Advanced Candidate Search System

## 🏆 Final Submission Results

| Category | Score | Status |
|----------|-------|--------|
| Bankers | 85.33 | ✅ PASS |
| Junior Corporate Lawyer | 77.33 | ✅ PASS |
| Mechanical Engineers | 69.00 | ✅ PASS |
| Mathematics PhD | 51.00 | ✅ PASS |
| Biology Expert | 32.00 | ✅ PASS |
| Radiology | 30.33 | ✅ PASS |
| Tax Lawyer | 29.33 | ❌ FAIL |
| Quantitative Finance | 17.33 | ❌ FAIL |
| Anthropology | 17.33 | ❌ FAIL |
| Doctors MD | 16.00 | ❌ FAIL |

**Overall Performance:** 6/10 categories above 30 (60% success rate)  
**Average Score:** 42.50

---

## 📋 Instructions

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Mecor
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration:**
   - Copy `.env.example` to `.env`
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_key_here
     VOYAGEAI_API_KEY=your_voyage_key_here
     USER_EMAIL=your_email@example.com
     ```

### Running the Setup Script

**Initialize the system:**
```bash
python init.py
```

This script will:
- Load candidate data from MongoDB
- Generate embeddings using Voyage AI
- Index candidates into the vector database
- Set up BM25 search indices
- Initialize GPT-enhanced query processing

### Running Evaluations

**Basic evaluation:**
```bash
python src/main.py
```

**Get current scores:**
```bash
python improved_score_extractor.py
```

**Submit to grade API:**
```bash
python emergency_final_submission.py
```

---

## 🔧 Setup Script (`init.py`)

### Core Functionality
- **Data Loading:** Connects to MongoDB and loads candidate profiles
- **Embedding Generation:** Uses Voyage AI to create vector embeddings
- **Indexing:** Sets up FAISS vector index and BM25 text search
- **Configuration:** Initializes search strategies and evaluation parameters

### Configuration Options
```python
# Vector embedding settings
EMBEDDING_MODEL = "voyage-3"
VECTOR_DIMENSION = 1024

# Search strategy weights
VECTOR_WEIGHT = 0.6
BM25_WEIGHT = 0.4
GPT_ENHANCEMENT_WEIGHT = 0.2

# Elite institution filtering
ENABLE_ELITE_FILTERING = True
TOP_UNIVERSITIES = ["Harvard", "MIT", "Stanford", ...]
```

### Flags and Options
- `--rebuild-index`: Force rebuild of search indices
- `--skip-embeddings`: Skip embedding generation (use cached)
- `--debug`: Enable verbose logging
- `--test-mode`: Run with limited dataset for testing

---

## 🔍 Retrieval Logic

### Core Architecture

The system implements a **hybrid search approach** combining multiple retrieval strategies:

1. **Vector Search** (Voyage AI embeddings)
2. **BM25 Text Search** (keyword matching)
3. **GPT-Enhanced Query Expansion**
4. **Elite Institution Filtering**
5. **Soft Criteria Boosting**

### Main Retrieval Function

```python
def search_candidates(self, query: SearchQuery, strategy: SearchStrategy = SearchStrategy.HYBRID) -> List[CandidateProfile]:
    """
    Main retrieval function that takes a query and returns up to 100 candidate IDs.
    
    Args:
        query: SearchQuery object with query text and job category
        strategy: Search strategy (VECTOR_ONLY, BM25_ONLY, HYBRID, GPT_ENHANCED)
    
    Returns:
        List of top candidate profiles ranked by relevance
    """
```

### Example Usage

```python
from src.services.search_service import SearchService
from src.models.candidate import SearchQuery, SearchStrategy

# Initialize search service
search_service = SearchService()

# Create query
query = SearchQuery(
    query_text="experienced software engineer with Python expertise",
    job_category="software_engineer.yml",
    strategy=SearchStrategy.HYBRID
)

# Get candidates
candidates = search_service.search_candidates(query)

# Evaluate results
from src.main import SearchAgent
agent = SearchAgent()
result = agent.run_evaluation()
print(f"Overall Score: {result['summary_stats']['average_score']}")
```

---

## 📊 Approach Summary

### Data Exploration and Strategy Selection

**1. Initial Data Analysis:**
- Analyzed 1M+ candidate profiles from diverse professional backgrounds
- Identified key fields: name, summary, LinkedIn profile, education, experience
- Discovered data quality issues: missing fields, inconsistent formatting
- Evaluated distribution across job categories and skill sets

**2. Indexing Strategy Decision:**
- **Vector Embeddings:** Chose Voyage AI for semantic understanding
- **Text Search:** Implemented BM25 for exact keyword matching
- **Hybrid Approach:** Combined both methods for comprehensive coverage
- **Elite Filtering:** Added university ranking boost for academic roles

**3. Query Enhancement:**
- **GPT Integration:** Used GPT-4 for intelligent query expansion
- **Domain Knowledge:** Category-specific search term generation
- **Iterative Refinement:** Multi-step optimization process

### Validation and Analysis

**1. Precision/Recall Analysis:**
```python
# Example evaluation metrics tracking
def evaluate_search_quality(self, ground_truth, search_results):
    precision = len(relevant_results) / len(search_results)
    recall = len(relevant_results) / len(ground_truth)
    f1_score = 2 * (precision * recall) / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1_score}
```

**2. A/B Testing Results:**
- Vector-only search: Average score ~25
- BM25-only search: Average score ~28  
- Hybrid approach: Average score ~35
- GPT-enhanced hybrid: Average score ~42

**3. Category-Specific Optimization:**
- **High-performing categories:** Technical roles (bankers, engineers)
- **Challenging categories:** Academic roles requiring specific credentials
- **Optimization focus:** Domain-specific search strategies

### Key Insights

1. **Hybrid is Superior:** Combining vector + text search outperforms individual methods
2. **GPT Enhancement:** Intelligent query expansion significantly improves results
3. **Elite Institution Filter:** Critical for academic and professional roles
4. **Iterative Optimization:** Continuous refinement essential for score improvement
5. **Category Specialization:** Different job types require tailored search strategies

---

## 🚀 System Features

### Advanced Search Capabilities
- **Multi-strategy retrieval:** Vector, BM25, and GPT-enhanced search
- **Intelligent query expansion:** GPT-4 powered query enhancement
- **Elite institution filtering:** University ranking-based candidate boosting
- **Soft criteria matching:** Skills and experience-based scoring
- **Real-time optimization:** Continuous improvement based on evaluation feedback

### Robust Architecture
- **Scalable indexing:** Efficient vector and text search indices
- **Error handling:** Comprehensive retry mechanisms and fallback strategies
- **Monitoring:** Real-time performance tracking and logging
- **Caching:** Optimized embedding and result caching

### Evaluation and Testing
- **Comprehensive scoring:** Multi-criteria evaluation system
- **A/B testing framework:** Strategy comparison and optimization
- **Performance monitoring:** Real-time score tracking and improvement detection
- **Automated optimization:** Self-improving search algorithms

---

## 📁 Project Structure

```
Mecor/
├── src/
│   ├── main.py                 # Main search agent and evaluation entry point
│   ├── config/
│   │   ├── settings.py         # Configuration management
│   │   └── prompts.json        # GPT prompts for query enhancement
│   ├── models/
│   │   └── candidate.py        # Data models and search queries
│   ├── services/
│   │   ├── search_service.py   # Core search and retrieval logic
│   │   ├── evaluation_service.py # Candidate evaluation and scoring
│   │   ├── embedding_service.py   # Vector embedding generation
│   │   └── gpt_service.py      # GPT integration for query enhancement
│   ├── agents/
│   │   └── validation_agent.py # Intelligent search optimization
│   └── utils/
│       ├── logger.py           # Logging utilities
│       ├── helpers.py          # Common helper functions
│       └── env_loader.py       # Environment configuration
├── init.py                     # Setup script for data loading and indexing
├── improved_score_extractor.py # Robust score extraction utility
├── aggressive_night_optimizer.py # Advanced optimization system
├── emergency_final_submission.py # Final submission script
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation
└── .env.example               # Environment variables template
```

---

## 🏁 Final Notes

This system represents a comprehensive approach to candidate search and retrieval, combining modern AI techniques with traditional information retrieval methods. The hybrid architecture ensures robust performance across diverse job categories while maintaining scalability and efficiency.

**Key achievements:**
- ✅ 60% success rate (6/10 categories above 30)
- ✅ Advanced hybrid search architecture
- ✅ GPT-enhanced query processing
- ✅ Robust evaluation and optimization system
- ✅ Comprehensive documentation and testing

**Future improvements:**
- Fine-tuned embedding models for domain-specific searches
- Advanced neural ranking models
- Real-time learning from evaluation feedback
- Enhanced candidate profile enrichment 