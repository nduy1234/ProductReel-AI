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

## Running the Green Agent

The Green Agent can be run in several ways depending on your needs. The main entry point is `eval/run_agentbeats.py`.

### Basic Command

The simplest way to run the Green Agent:

```bash
python eval/run_agentbeats.py --config configs/gaia_agent.yaml
```

This will:
- Load tasks from the data source specified in the config file
- Execute each task using the Plan → Act → Verify → Answer loop
- Save results to the `results/` directory
- Generate a summary of all evaluations

### Command-Line Options

The Green Agent supports several command-line arguments:

| Option | Description | Example |
|--------|-------------|---------|
| `--config` | Path to YAML configuration file (required) | `--config configs/gaia_agent.yaml` |
| `--data-source` | Override data source from config | `--data-source data/sample_gaia_tasks.json` |
| `--data-format` | Data format: `json`, `jsonl`, `parquet`, or `huggingface` | `--data-format json` |
| `--task-id` | Run a single specific task | `--task-id "task_123"` |
| `--max-tasks` | Limit number of tasks to process | `--max-tasks 10` |
| `--output-dir` | Custom output directory for results | `--output-dir "my_results"` |

### Common Use Cases

#### 1. Test with Sample Data

Run the agent on the included sample tasks:

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --data-source data/sample_gaia_tasks.json \
  --data-format json \
  --max-tasks 5
```

#### 2. Run a Single Task

Execute one specific task by ID:

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --task-id "task_1"
```

#### 3. Batch Evaluation

Process multiple tasks from a local file:

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --data-source path/to/gaia_tasks.json \
  --data-format json \
  --max-tasks 100
```

#### 4. Use Hugging Face Dataset

Load tasks from a Hugging Face dataset:

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --data-source "gaia-benchmark/GAIA" \
  --data-format huggingface
```

#### 5. Custom Output Location

Save results to a specific directory:

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --output-dir "experiments/run_001"
```

### What Happens When You Run the Agent

1. **Initialization**: The agent loads configuration, initializes tools (calculator), and sets up logging
2. **Task Loading**: Tasks are loaded from the specified data source
3. **Execution Loop**: For each task:
   - **Planning**: Problem is decomposed into steps
   - **Action**: Tools are invoked to perform computations
   - **Verification**: Results are checked at each step
   - **Answer**: Final answer is generated and verified
4. **Results**: Individual task results and summary are saved to JSON files

### Output Files

After running, you'll find:

- **Individual Results**: `results/{task_id}.json` - Detailed execution log for each task
- **Summary**: `results/summary.json` - Overall statistics (accuracy, counts, etc.)
- **Logs**: Console output shows progress and execution details

### Example Output

When running, you'll see output like:

```
Loading tasks from data/sample_gaia_tasks.json...
Loaded 5 tasks
Running task: task_1
  Planning: Identified 1 step(s)
  Action: Executing step 1...
  Verification: Step 1 passed
  Answer: 42
  Result: ✓ Correct
...
Summary: 4/5 tasks correct (80.0% accuracy)
Results saved to results/
```

### Running in Python Code

You can also run the Green Agent programmatically:

```python
from agent import GAIAAgent
from tasks import GAIALoader
from tools import Calculator

# Initialize agent
calculator = Calculator(precision=50)
agent = GAIAAgent(calculator=calculator, seed=42)

# Load a task
loader = GAIALoader()
task = loader.get_task("task_1", source="data/sample_gaia_tasks.json", format="json")

# Execute
result = agent.execute(task.prompt)
print(f"Answer: {result['answer']}")
```

See `example_usage.py` for a complete example.

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

This implementation follows AgentBeats licensing. GAIA dataset has its own license terms.

## Docker Deployment

### Build Docker Image

```bash
# Linux/Mac
./build_docker.sh

# Windows
build_docker.bat

# Or manually
docker build -t gaia-green-agent:latest .
```

### Run Green Agent

```bash
docker run -v $(pwd)/results:/app/results gaia-green-agent:latest
```

### Run Purple Agent Server

```bash
docker run -p 8000:8000 gaia-green-agent:latest python -m purple_agent.server
```

### Using Docker Compose

```bash
docker-compose up
```

This starts both:
- Green Agent (evaluation runner)
- Purple Agent (A2A endpoint on port 8000)

## Submission Components

This project includes:

1. **Green Agent**: Complete implementation (`agent/`, `tools/`, `tasks/`, `eval/`)
2. **Baseline Purple Agent**: A2A-compatible participant agent (`purple_agent/`)
3. **Docker Image**: Containerized deployment (see `Dockerfile`)
4. **Documentation**: Comprehensive guides (see `ABSTRACT.md`)

## Citation

If you use GAIA benchmark, please cite:

```bibtex
@article{gaia2023,
  title={GAIA: a benchmark for General AI Assistants},
  author={Mialon, Grégoire and others},
  journal={arXiv preprint arXiv:2311.12983},
  year={2023}
}
```

## Resources

- **GAIA Benchmark**: https://huggingface.co/datasets/gaia-benchmark/GAIA
- **GAIA Leaderboard**: https://huggingface.co/spaces/gaia-benchmark/leaderboard
- **AgentBeats Platform**: https://agentbeats.org
- **A2A Protocol**: https://github.com/agentbeats/a2a-sdk

