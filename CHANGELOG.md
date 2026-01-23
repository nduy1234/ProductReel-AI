# Changelog

## [1.1.0] - 2026-01-22

### Added
- **Multi-step problem handling**: The planner now detects sequential operations using patterns like:
  - "X, then Y"
  - "X then Y"
  - "X, and then Y"
  - "first X, then Y"
  - "X, after that Y"
- **Intermediate result chaining**: The agent automatically chains results from previous computation steps
- **Enhanced operation detection**: Better recognition of word-based operations ("add", "subtract", "multiply by", "divide by")
- **Comprehensive test suite**: Added `test_multi_step.py` with 5 test cases covering various multi-step scenarios
- **Extended sample data**: Added 3 new multi-step test cases to `data/sample_gaia_tasks.json`

### Improved
- **Answer generation**: Now correctly uses the final result from multi-step computations
- **Planner accuracy**: Better pattern matching for sequential operations
- **Unicode compatibility**: Fixed encoding issues with special characters in Windows console

### Fixed
- Multi-step problems like "Calculate 15 multiplied by 7, then add 23" now correctly compute 128 (previously only computed 105)
- Intermediate results are now properly passed between computation steps

## [1.0.0] - 2026-01-22

### Initial Release
- Core agent implementation with Plan → Act → Verify → Answer loop
- Calculator tool with deterministic arithmetic
- GAIA benchmark loader (JSON, JSONL, Parquet, Hugging Face)
- AgentBeats task wrapper and evaluation
- Basic single-step problem solving
- Comprehensive documentation
