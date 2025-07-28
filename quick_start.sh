#!/bin/bash

# Advanced Search Agent - Quick Start Script
# This script loads environment variables from .env and runs the search agent

echo "🚀 Advanced Search Agent - Quick Start"
echo "======================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Please activate your virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo "❌ Error: .env file not found!"
    echo "   Please copy environment_template.txt to .env and fill in your API keys:"
    echo "   cp environment_template.txt .env"
    echo "   # Then edit .env with your actual API keys"
    exit 1
fi

# Load environment variables from .env file
echo "🔧 Loading environment variables from .env file..."
set -a  # Export all variables
source .env
set +a  # Stop exporting

# Verify required environment variables are set
required_vars=("VOYAGE_API_KEY" "TURBOPUFFER_API_KEY" "OPENAI_API_KEY" "USER_EMAIL" "TURBOPUFFER_NAMESPACE")

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "❌ Error: Required environment variable $var is not set in .env file"
        exit 1
    fi
done

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