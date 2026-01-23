# GAIA Green Agent for AgentBeats

A fully reproducible, tool-using agent that converts static GAIA math problems into executable agent workflows compatible with the AgentBeats framework.

## Overview

This project ports and extends the GAIA benchmark into a **Green Agent** that runs end-to-end on AgentBeats. The agent demonstrates:

- **Verifiable reasoning**: Clear separation of planning, acting, and verification
- **Tool-grounded computation**: Explicit tool invocation for mathematical operations
- **Deterministic execution**: Reproducible results given a fixed seed
- **AgentBeats compatibility**: Conforms to AgentBeats interfaces and protocols

## Architecture

The agent follows a structured **Plan → Act → Verify → Answer** loop:

1. **Planning**: Parse the GAIA problem and decompose into ordered reasoning steps
2. **Action**: Call mathematical tools when needed (calculator, symbolic solver)
3. **Verification**: Check intermediate and final results
4. **Answer**: Emit a concise, structured final answer

### Directory Structure

```
.
├── agent/              # Core agent logic
│   ├── agent.py       # Main agent with Plan→Act→Verify→Answer loop
│   ├── planner.py     # Task decomposition
│   └── verifier.py    # Answer checking
├── tools/              # Agent tools
│   └── calculator.py  # Deterministic calculator
├── tasks/              # Task loaders and wrappers
│   ├── gaia_loader.py # Load GAIA benchmark
│   └── gaia_task.py   # AgentBeats task wrapper
├── eval/               # Evaluation scripts
│   └── run_agentbeats.py  # End-to-end execution
└── configs/            # Configuration files
    └── gaia_agent.yaml # Agent configuration
```

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: The minimum required dependency is `pyyaml`. For full functionality:
- `pandas` and `pyarrow` for Parquet file support
- `datasets` for Hugging Face dataset support

For basic usage with JSON files, only `pyyaml` is needed:
```bash
pip install pyyaml
```

3. (Optional) For Hugging Face dataset support:
```bash
pip install datasets
```

4. (Optional) For Parquet file support:
```bash
pip install pandas pyarrow
```

## Quick Start

1. **Test with sample data** (no external dependencies needed):
```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --data-source data/sample_gaia_tasks.json \
  --data-format json \
  --max-tasks 5
```

2. **Run the example script**:
```bash
python example_usage.py
```

## Usage

### Basic Usage

Run evaluation with default configuration:

```bash
python eval/run_agentbeats.py --config configs/gaia_agent.yaml
```

### Running a Single Task

```bash
python eval/run_agentbeats.py --config configs/gaia_agent.yaml --task-id "task_123"
```

### Running with Custom Data Source

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --data-source "path/to/gaia_data.json" \
  --data-format json
```

### Running with Hugging Face Dataset

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --data-source "gaia-benchmark/GAIA" \
  --data-format huggingface
```

### Limiting Number of Tasks

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --max-tasks 10
```

### Custom Output Directory

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --output-dir "my_results"
```

## Configuration

Edit `configs/gaia_agent.yaml` to customize:

- **Agent settings**: Seed, retry limits, calculator precision
- **Data source**: File path or Hugging Face dataset
- **Filtering**: Math-only tasks, specific difficulty levels
- **Output**: Results directory, logging options

### Example Configuration

```yaml
agent:
  seed: 42
  max_retries: 3
  calculator_precision: 50

data:
  source: "gaia-benchmark/GAIA"
  format: "huggingface"
  split: "validation"
  filter_math_only: true
  level: 1  # Only level 1 tasks

evaluation:
  output_dir: "results"
```

## How GAIA Was Agentified

### From Static Problems to Agent Workflows

1. **Problem Parsing**: GAIA problems are loaded and normalized into a standard format
2. **Task Decomposition**: The planner analyzes each problem and identifies:
   - Required mathematical operations
   - Numbers and values to extract
   - Tool requirements
   - Execution order
3. **Tool Integration**: Mathematical operations are executed via explicit tool calls (calculator)
4. **Verification**: Each step and the final answer are verified for correctness
5. **Answer Generation**: A concise final answer is produced (no hidden chain-of-thought)

### Key Extensions Beyond Baseline GAIA

1. **Structured Agent Loop**: Clear separation of planning, action, verification phases
2. **Tool-Grounded Computation**: All math operations use explicit tool invocations
3. **Deterministic Execution**: Reproducible results with fixed seeds
4. **Verification System**: Multi-level verification (step-level and answer-level)
5. **AgentBeats Compatibility**: Full integration with AgentBeats task and response formats
6. **Comprehensive Logging**: Machine-readable JSON logs for all execution phases
7. **Multi-Step Problem Handling**: Detects and chains sequential operations (e.g., "X then Y", "first X, then Y")
8. **Intermediate Result Chaining**: Automatically uses results from previous steps in subsequent computations

## AgentBeats Compatibility

The agent conforms to AgentBeats interfaces:

- **Task Definition**: Uses `AgentBeatsTask` dataclass compatible with A2A protocol
- **Agent Step Loop**: Implements standard agent execution cycle
- **Tool Invocation**: Tools are explicitly invoked and logged
- **Episode Termination**: Clear termination conditions and answer emission
- **Output Format**: Results in AgentBeats-readable evaluation format

## Evaluation Results

Results are saved in JSON format:

- **Individual task results**: `{task_id}.json` files with full execution details
- **Summary**: `summary.json` with overall statistics (accuracy, correct/incorrect counts)

### Result Format

```json
{
  "task_id": "task_123",
  "response": {
    "answer": "42",
    "verified": true,
    "metadata": {
      "plan": {...},
      "steps_count": 3,
      "execution_log": [...]
    }
  },
  "evaluation": {
    "correct": true,
    "score": 1.0,
    "message": "Exact match"
  }
}
```

## Design Philosophy

This agent demonstrates:

- **Verifiable Reasoning**: Every computation step is logged and verifiable
- **Tool-Grounded Computation**: No free-form guessing; all math uses tools
- **Clear Separation**: Planning, acting, and checking are distinct phases
- **Green Agent Criteria**: Stateless, deterministic, non-adversarial

## Constraints

As specified:

- ✅ No model fine-tuning
- ✅ No modification of GAIA ground truth
- ✅ No hidden chain-of-thought in outputs
- ✅ Focus on agent execution quality, not prompt cleverness

## Extending the Agent

### Adding New Tools

1. Create tool class in `tools/` directory
2. Implement tool interface with `evaluate()` or similar method
3. Register tool in agent's tool registry
4. Update planner to identify when tool should be used

### Supporting More GAIA Task Types

1. Extend `GAIALoader` to handle additional file types or formats
2. Update `Planner` to recognize new problem patterns
3. Add specialized tools if needed (e.g., image processing, web browsing)

### Improving Verification

1. Enhance `Verifier` with domain-specific checks
2. Add unit tests for verification logic
3. Implement more sophisticated answer normalization

## Troubleshooting

### Import Errors

If you see import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Data Loading Issues

- For Hugging Face datasets: Ensure you have access (some datasets are gated)
- For local files: Check file paths are correct and files exist
- For Parquet files: Install `pandas` and `pyarrow`

### Calculator Errors

The calculator uses Python's `eval()` which can be restrictive. For complex expressions, consider:
- Using a proper expression parser (e.g., `sympy`)
- Breaking complex expressions into simpler sub-expressions

## License

This project is provided as-is for research and evaluation purposes.

## Citation

If you use this code, please cite:
- GAIA Benchmark: [arXiv:2311.12983](https://arxiv.org/abs/2311.12983)
- AgentBeats: [docs.agentbeats.org](https://docs.agentbeats.org/)
