# Quick Start Guide

Get up and running with the GAIA Green Agent in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Step 1: Install Dependencies

```bash
# Minimum required (for JSON files)
pip install PyYAML

# Or install all dependencies
pip install -r requirements.txt
```

## Step 2: Test the Agent

Run the example script to verify everything works:

```bash
python example_usage.py
```

Expected output:
- Agent initializes successfully
- Processes a multi-step problem: "Calculate 15 multiplied by 7, then add 23"
- Returns answer: 128
- Shows execution steps and verification

## Step 3: Run Multi-Step Tests

Verify multi-step problem handling:

```bash
python test_multi_step.py
```

Expected: All 5 tests pass (100% success rate)

## Step 4: Run Evaluation (Optional)

If you have PyYAML installed, run the full evaluation:

```bash
python eval/run_agentbeats.py --config configs/gaia_agent.yaml --max-tasks 3
```

## What You Should See

### Example Script Output
```
Initializing GAIA Agent...
Problem: Calculate 15 multiplied by 7, then add 23. What is the result?
Executing agent...
Final Answer: 128
Verified: True
Steps Executed: 2
  Step 1: 15 * 7 = 105
  Step 2: 105 + 23 = 128
```

### Test Suite Output
```
MULTI-STEP PROBLEM TESTING
Total tests: 5
Passed: 5
Failed: 0
Success rate: 100.0%
```

## Troubleshooting

### Import Errors
- Ensure you're in the project root directory
- Check Python version: `python --version` (should be 3.8+)

### Module Not Found
- Verify you're running from the correct directory
- Check that all `__init__.py` files exist in subdirectories

### PyYAML Not Found (for evaluation runner)
- Install: `pip install PyYAML`
- Or use the example/test scripts which don't require it

## Next Steps

1. **Try your own problems**: Modify `example_usage.py` with custom math problems
2. **Add more test cases**: Extend `test_multi_step.py` with additional scenarios
3. **Use real GAIA data**: Point the evaluation runner to actual GAIA dataset files
4. **Extend functionality**: Add new tools or improve the planner

## Project Structure Overview

```
.
├── agent/              # Core agent (Plan→Act→Verify→Answer)
├── tools/              # Calculator tool
├── tasks/              # GAIA loaders and wrappers
├── eval/               # Evaluation scripts
├── configs/            # Configuration files
├── data/               # Sample test data
├── example_usage.py    # Simple usage example
├── test_multi_step.py  # Multi-step test suite
└── README.md           # Full documentation
```

## Key Features Demonstrated

✅ Single-step math problems  
✅ Multi-step sequential operations  
✅ Intermediate result chaining  
✅ Tool-grounded computation  
✅ Verification at each step  
✅ AgentBeats compatibility  

You're all set! 🚀
