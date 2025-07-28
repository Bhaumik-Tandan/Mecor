#!/bin/bash

# Advanced Search Agent - Quick Start Script
# This script sets up environment variables and runs the search agent

echo "🚀 Advanced Search Agent - Quick Start"
echo "======================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Please activate your virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

# Set up environment variables with your API keys
export VOYAGE_API_KEY="***REMOVED***"
export TURBOPUFFER_API_KEY="***REMOVED***"
export OPENAI_API_KEY="***REMOVED***"
export TURBOPUFFER_NAMESPACE="***REMOVED***"
export USER_EMAIL="bhaumik.tandan@gmail.com"

# Default settings for optimal performance
export MAX_CANDIDATES_PER_QUERY="100"
export VECTOR_SEARCH_WEIGHT="0.6"
export BM25_SEARCH_WEIGHT="0.4"
export SOFT_FILTER_WEIGHT="0.2"
export THREAD_POOL_SIZE="5"

echo "✅ Environment configured successfully"
echo ""

# Check if user wants to run a specific command
if [ $# -eq 0 ]; then
    echo "🔍 Running full evaluation with hybrid search..."
    python3 -m src.main --max-workers 5
else
    echo "🎯 Running custom command: $@"
    python3 -m src.main "$@"
fi

echo ""
echo "🎉 Search Agent execution completed!"
echo "📊 Check the 'results/' directory for detailed output" 