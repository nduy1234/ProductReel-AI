# GAIA Green Agent Architecture

## System Overview

The GAIA Green Agent is a fully reproducible, tool-using agent that converts static GAIA math problems into executable agent workflows compatible with the AgentBeats framework.

## Core Components

### 1. Agent Loop (`agent/agent.py`)

The `GAIAAgent` class implements the core Plan → Act → Verify → Answer loop:

```
┌─────────┐
│  PLAN   │  ← Parse problem, decompose into steps
└────┬────┘
     │
     ▼
┌─────────┐
│  ACT    │  ← Execute steps using tools
└────┬────┘
     │
     ▼
┌─────────┐
│ VERIFY  │  ← Check intermediate and final results
└────┬────┘
     │
     ▼
┌─────────┐
│ ANSWER  │  ← Emit structured final answer
└─────────┘
```

**Key Features:**
- Stateless across episodes (except logs)
- Deterministic given a fixed seed
- Non-adversarial (Green Agent criteria)
- Tool-grounded computation

### 2. Planner (`agent/planner.py`)

The `Planner` class analyzes GAIA problems and creates execution plans:

- **Pattern Recognition**: Identifies mathematical operations in natural language
- **Step Decomposition**: Breaks problems into ordered execution steps
- **Tool Selection**: Determines which tools are needed
- **Context Extraction**: Extracts numbers and expressions from text

**Supported Patterns:**
- Explicit operations: "15 multiplied by 7"
- Word operators: "plus", "minus", "times", "divided by"
- Complex expressions: "(2 + 3) * 4"
- Calculation requests: "calculate", "compute", "find"

### 3. Verifier (`agent/verifier.py`)

The `Verifier` class performs multi-level verification:

- **Step Verification**: Checks each computation step
- **Answer Verification**: Validates final answer format and correctness
- **Retry Logic**: Determines when to retry failed steps
- **Normalization**: Extracts core answer from verbose responses

**Verification Levels:**
1. Step-level: Each tool call result is verified
2. Answer-level: Final answer format and sanity checks
3. Comparison-level: Answer compared to ground truth (in evaluation)

### 4. Calculator Tool (`tools/calculator.py`)

A deterministic calculator using Python's `decimal` module:

- **Precise Arithmetic**: Uses Decimal for exact calculations
- **Safe Evaluation**: Custom parser avoids `eval()` security issues
- **Operator Support**: +, -, *, /, parentheses, operator precedence
- **Error Handling**: Graceful failure with error messages

**Implementation:**
- Tokenizer: Converts expression string to tokens
- Parser: Handles parentheses and operator precedence
- Evaluator: Performs arithmetic with Decimal precision

### 5. GAIA Loader (`tasks/gaia_loader.py`)

Loads GAIA benchmark data from multiple formats:

- **JSON/JSONL**: Standard file formats
- **Parquet**: Efficient columnar format (requires pandas)
- **Hugging Face**: Direct dataset loading (requires datasets library)

**Normalization:**
- Standardizes field names across formats
- Handles different GAIA dataset versions
- Extracts metadata consistently

### 6. AgentBeats Task Wrapper (`tasks/gaia_task.py`)

Converts between GAIA and AgentBeats formats:

- **Task Conversion**: GAIA → AgentBeatsTask
- **Response Formatting**: Agent results → AgentBeats response
- **Evaluation**: Compares answers to ground truth

**AgentBeats Compatibility:**
- Follows A2A protocol for task management
- Produces machine-readable evaluation results
- Supports batch execution

### 7. Evaluation Runner (`eval/run_agentbeats.py`)

End-to-end evaluation script:

- **Configuration Loading**: YAML-based configuration
- **Batch Processing**: Run multiple tasks
- **Result Saving**: JSON output for each task and summary
- **Logging**: Comprehensive execution logs

## Data Flow

```
GAIA Dataset
    ↓
GAIALoader
    ↓
AgentBeatsTask
    ↓
GAIAAgent.execute()
    ↓
  ├─→ Planner.plan()
  │     ↓
  │   Execution Steps
  │     ↓
  ├─→ Calculator.evaluate()
  │     ↓
  ├─→ Verifier.verify_step()
  │     ↓
  └─→ Verifier.verify_final_answer()
        ↓
    Final Answer
        ↓
    Evaluation
        ↓
    Results (JSON)
```

## Tool Architecture

### Current Tools

1. **Calculator** (`tools/calculator.py`)
   - Deterministic arithmetic operations
   - Supports basic math: +, -, *, /
   - Handles operator precedence
   - Uses Decimal for precision

### Extending Tools

To add a new tool:

1. Create tool class in `tools/` directory
2. Implement interface:
   ```python
   class MyTool:
       def evaluate(self, input: str) -> Dict[str, Any]:
           # Return {'result': ..., 'success': bool}
   ```
3. Register in agent (update `_execute_step`)
4. Update planner to identify when tool is needed

## Logging and Observability

### Execution Log Structure

Each execution produces a structured log:

```json
{
  "phase": "start|plan|step|answer|complete",
  "timestamp": "ISO8601",
  "task_id": "...",
  "data": {...}
}
```

### Log Phases

1. **start**: Task initialization
2. **plan**: Planning phase results
3. **step**: Individual step execution
4. **answer**: Final answer generation
5. **complete**: Execution summary

## Determinism and Reproducibility

### Seed Management

- Agent accepts a `seed` parameter
- Planner uses seed for any random operations (currently none)
- Calculator is deterministic by design
- All operations are deterministic given same inputs

### Stateless Design

- Agent resets between episodes
- No persistent state across tasks
- Logs are per-episode only
- Tools are stateless

## AgentBeats Integration

### Task Format

```python
AgentBeatsTask(
    task_id: str,
    task_type: str,
    prompt: str,
    metadata: Dict,
    ground_truth: Optional[str]
)
```

### Response Format

```python
{
    'task_id': str,
    'answer': str,
    'verified': bool,
    'metadata': {
        'plan': {...},
        'steps_count': int,
        'execution_log': [...]
    }
}
```

### Evaluation Format

```python
{
    'correct': bool,
    'score': float,  # 0.0 to 1.0
    'message': str
}
```

## Extensions Beyond Baseline GAIA

1. **Structured Agent Loop**: Clear separation of planning, action, verification
2. **Tool-Grounded Computation**: Explicit tool invocations for all math
3. **Deterministic Execution**: Reproducible with fixed seeds
4. **Verification System**: Multi-level verification (step + answer)
5. **AgentBeats Compatibility**: Full A2A protocol support
6. **Comprehensive Logging**: Machine-readable JSON logs
7. **Safe Calculator**: Custom parser avoids eval() security issues
8. **Multi-Format Support**: JSON, JSONL, Parquet, Hugging Face

## Future Enhancements

### Potential Improvements

1. **Enhanced Planner**:
   - Multi-step problem decomposition
   - Better natural language understanding
   - Support for word problems with multiple operations

2. **Additional Tools**:
   - Symbolic math solver (sympy integration)
   - Unit conversion
   - Statistical operations

3. **Better Verification**:
   - Semantic answer matching
   - Tolerance-based numeric comparison
   - Partial credit scoring

4. **Performance**:
   - Parallel task execution
   - Caching of common computations
   - Optimized expression parsing

## Testing Strategy

### Unit Tests (Recommended)

- Calculator: Test arithmetic operations, precedence, edge cases
- Planner: Test pattern recognition, step generation
- Verifier: Test answer normalization, comparison logic
- Agent: Test full loop with mock tools

### Integration Tests

- End-to-end with sample GAIA tasks
- AgentBeats format conversion
- Batch evaluation

### Example Test Cases

```python
# Calculator
assert calculator.evaluate("2 + 3 * 4") == "14"
assert calculator.evaluate("(2 + 3) * 4") == "20"

# Planner
plan = planner.plan("What is 15 times 7?")
assert plan['requires_tools'] == True
assert len(plan['steps']) > 0

# Verifier
verification = verifier.verify_final_answer("42", "What is 6 * 7?")
assert verification['valid'] == True
```

## Performance Considerations

### Current Limitations

- Single-threaded execution
- No caching of computations
- Simple pattern matching (not LLM-based)

### Optimization Opportunities

- Parallel task execution
- Expression result caching
- More efficient parsing algorithms

## Security Considerations

### Calculator Safety

- Custom parser avoids `eval()` security risks
- Input sanitization before parsing
- Restricted character set
- No code execution

### Input Validation

- Expression sanitization
- Type checking
- Error handling for malformed inputs
