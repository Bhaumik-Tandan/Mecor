# Mercor Interview Testing Guide

## 🚀 Quick Start

### 1. Pre-Interview Setup
```bash
# Validate your system is ready
python interview_setup.py

# If everything passes, you're ready!
```

### 2. During the Interview

#### Option A: Interactive Mode (Recommended)
```bash
python interview_testing_script.py --interactive
```
- Type queries as they give them to you
- See results immediately
- Type `help` for commands, `quit` to exit

#### Option B: Single Query Testing
```bash
python interview_testing_script.py --query "experienced tax lawyer"
python interview_testing_script.py --query "quantitative finance expert" --category "quantitative_finance.yml"
```

#### Option C: Batch Testing (if they give multiple queries)
```bash
# Create a file with their queries
echo "query1" > interview_queries.txt
echo "query2" >> interview_queries.txt

# Run batch test
python interview_testing_script.py --batch-file interview_queries.txt
```

## 📋 What the Script Does

1. **Search Phase**: Finds relevant candidates using your optimized hybrid search
2. **Evaluation Phase**: Evaluates top candidates using Mercor's API
3. **Results**: Shows number of candidates found and average score

## 🎯 Expected Output

```
🧪 Testing query: 'experienced tax lawyer'
✅ Search completed: 15 candidates found
✅ Evaluation completed: Score = 0.847
✅ Test completed successfully
📊 Found 15 candidates
🎯 Average Score: 0.847
⏱️  Total time: 3.24s
```

## 🔧 Troubleshooting

### If the script fails to start:
```bash
# Check environment
python interview_setup.py

# Install missing packages
pip install -r requirements.txt
```

### If search returns no results:
- Try a more general query
- Check if the category is correct
- The system will auto-detect categories if not specified

### If evaluation fails:
- This is normal for some queries
- The search results are still valid
- Focus on the number of candidates found

## 💡 Interview Tips

1. **Start with interactive mode** - it's the most flexible
2. **Keep it simple** - use natural language queries
3. **Don't worry about categories** - the system auto-detects them
4. **Focus on results** - show them the candidates found and scores
5. **Be prepared for edge cases** - some queries might not return results

## 📁 File Structure

```
Mecor/
├── interview_testing_script.py    # Main testing script
├── interview_setup.py             # Setup validation
├── example_queries.txt            # Example queries
├── INTERVIEW_GUIDE.md             # This guide
├── src/                           # Your existing system
└── interview_results/             # Results will be saved here
```

## 🚨 Emergency Commands

If something goes wrong during the interview:

```bash
# Quick system check
python interview_setup.py

# Test with a simple query
python interview_testing_script.py --query "software engineer"

# Check logs
tail -f logs/interview_testing.log
```

## 📊 Understanding Results

- **Number of candidates**: How many relevant profiles were found
- **Average score**: Quality of the matches (0.0 to 1.0, higher is better)
- **Total time**: How long the search + evaluation took

## 🎯 Success Metrics

- **Good**: 10+ candidates, score > 0.7
- **Excellent**: 20+ candidates, score > 0.8
- **Outstanding**: 30+ candidates, score > 0.9

Remember: The goal is to demonstrate that your system can find relevant candidates quickly and accurately! 