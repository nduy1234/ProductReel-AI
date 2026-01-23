# Evaluation Methodology

This document describes the comprehensive evaluation methodology for the GAIA Green Agent benchmark, including scoring criteria, metrics, and evaluation dimensions.

## Overview

The GAIA Green Agent evaluates mathematical problem-solving capabilities through a structured Plan → Act → Verify → Answer loop. The evaluation methodology is designed to be:

- **Objective**: Clear, automated scoring criteria
- **Nuanced**: Goes beyond binary pass/fail
- **Multi-dimensional**: Captures accuracy, efficiency, safety, and reasoning quality
- **Reproducible**: Deterministic results with fixed seeds
- **Automated**: Fully automated evaluation pipeline

## Scoring Criteria

### Primary Metrics

#### 1. Accuracy (0.0 - 1.0)

The primary metric for correctness:

- **Exact Match (1.0)**: Answer exactly matches ground truth after normalization
- **Numeric Match (1.0)**: Numeric answers match within tolerance (1e-6)
- **Partial Match (0.5)**: Answer contains ground truth or vice versa
- **No Match (0.0)**: Answer does not match ground truth

**Normalization Process**:
- Convert to lowercase
- Remove common prefixes ("the answer is", "answer:", etc.)
- Remove punctuation (except decimal points and minus signs)
- Extract numeric values when applicable

#### 2. Verification Status (Boolean)

Indicates whether the agent's internal verification passed:
- **Verified (True)**: Agent verified the answer as valid
- **Unverified (False)**: Agent could not verify the answer

#### 3. Execution Quality (0.0 - 1.0)

Measures the quality of the execution process:

- **Step Success Rate**: Percentage of steps that completed successfully
- **Tool Invocation Success**: Percentage of tool calls that succeeded
- **Retry Efficiency**: Whether retries were needed and if they succeeded

**Calculation**:
```
execution_quality = (
    (successful_steps / total_steps) * 0.4 +
    (successful_tool_calls / total_tool_calls) * 0.4 +
    (1.0 if no_retries_needed else 0.5 if retries_succeeded else 0.0) * 0.2
)
```

#### 4. Answer Format Quality (0.0 - 1.0)

Evaluates the format and structure of the answer:

- **Valid Format (1.0)**: Answer is properly formatted (numeric for math problems)
- **Acceptable Format (0.7)**: Answer format is acceptable but not ideal
- **Invalid Format (0.0)**: Answer format is invalid (too long, contains reasoning, etc.)

#### 5. Efficiency Metrics

- **Execution Time**: Time taken to complete the task (seconds)
- **Step Count**: Number of execution steps required
- **Tool Invocation Count**: Number of tool calls made
- **Retry Count**: Number of retry attempts

### Composite Score

The overall evaluation score combines multiple dimensions:

```
composite_score = (
    accuracy * 0.5 +
    execution_quality * 0.2 +
    answer_format_quality * 0.15 +
    (1.0 if verified else 0.0) * 0.15
)
```

## Evaluation Dimensions

### 1. Accuracy Dimension

**Purpose**: Measure correctness of final answers

**Metrics**:
- Exact match rate
- Numeric match rate (with tolerance)
- Partial match rate
- Overall accuracy percentage

**Evaluation**:
- Compares normalized agent answer to normalized ground truth
- Supports both exact and approximate matching
- Handles numeric and text-based answers

### 2. Efficiency Dimension

**Purpose**: Measure resource usage and execution speed

**Metrics**:
- Average execution time per task
- Average number of steps per task
- Average tool invocations per task
- Memory usage (if available)

**Benchmarks**:
- **Fast**: < 1 second per task
- **Moderate**: 1-5 seconds per task
- **Slow**: > 5 seconds per task

### 3. Robustness Dimension

**Purpose**: Measure reliability and error handling

**Metrics**:
- Task completion rate (successful / total)
- Step success rate
- Tool invocation success rate
- Retry success rate
- Error recovery rate

**Evaluation**:
- Tracks failures at each stage
- Measures recovery from errors
- Evaluates retry effectiveness

### 4. Reasoning Quality Dimension

**Purpose**: Measure the quality of the planning and execution process

**Metrics**:
- Plan quality (number of steps, appropriateness)
- Step ordering correctness
- Intermediate result accuracy
- Verification effectiveness

**Evaluation**:
- Analyzes execution logs
- Evaluates plan structure
- Checks step dependencies

### 5. Safety Dimension

**Purpose**: Measure adherence to safety constraints

**Metrics**:
- No code execution violations
- Input sanitization effectiveness
- Tool safety compliance
- Deterministic behavior

**Evaluation**:
- Verifies no eval() usage on user input
- Checks input sanitization
- Validates deterministic execution

## Task Difficulty Progression

### Level 1: Basic Arithmetic

**Characteristics**:
- Single-step operations
- Simple numbers (< 100)
- Direct computation required

**Examples**:
- "What is 15 multiplied by 7?"
- "Calculate 42 divided by 6."

**Expected Performance**:
- Accuracy: > 95%
- Execution time: < 0.5 seconds
- Steps: 1

### Level 2: Multi-Step Operations

**Characteristics**:
- Sequential operations
- Intermediate results
- Result chaining required

**Examples**:
- "Calculate 15 multiplied by 7, then add 23."
- "What is 20 divided by 4, then subtract 3?"

**Expected Performance**:
- Accuracy: > 90%
- Execution time: < 1 second
- Steps: 2-3

### Level 3: Complex Problems

**Characteristics**:
- Multiple operations with dependencies
- Complex expressions
- Requires careful planning

**Examples**:
- "First calculate 12 multiplied by 3, then add 14, then divide by 2."
- Complex word problems with multiple steps

**Expected Performance**:
- Accuracy: > 80%
- Execution time: < 2 seconds
- Steps: 3+

## Automated Evaluation

### Evaluation Pipeline

1. **Task Loading**: Load tasks from data source
2. **Agent Execution**: Run agent on each task
3. **Result Collection**: Gather execution results and logs
4. **Evaluation**: Compare answers to ground truth
5. **Metric Calculation**: Compute all evaluation metrics
6. **Summary Generation**: Generate aggregate statistics

### Evaluation Output

Each task produces:

```json
{
  "task_id": "task_123",
  "response": {
    "answer": "42",
    "verified": true,
    "metadata": {
      "plan": {...},
      "steps_count": 2,
      "execution_log": [...]
    }
  },
  "evaluation": {
    "correct": true,
    "score": 1.0,
    "message": "Exact match",
    "dimensions": {
      "accuracy": 1.0,
      "execution_quality": 1.0,
      "answer_format_quality": 1.0,
      "efficiency": {
        "execution_time": 0.234,
        "step_count": 2,
        "tool_invocations": 2
      },
      "robustness": {
        "completion": true,
        "step_success_rate": 1.0,
        "retry_count": 0
      }
    }
  }
}
```

### Summary Statistics

Aggregate metrics across all tasks:

```json
{
  "total_tasks": 100,
  "correct": 85,
  "incorrect": 15,
  "accuracy": 0.85,
  "average_score": 0.87,
  "dimension_averages": {
    "accuracy": 0.85,
    "execution_quality": 0.92,
    "answer_format_quality": 0.95,
    "efficiency": {
      "avg_execution_time": 0.45,
      "avg_step_count": 1.8,
      "avg_tool_invocations": 1.8
    },
    "robustness": {
      "completion_rate": 0.98,
      "avg_step_success_rate": 0.96,
      "avg_retry_count": 0.1
    }
  },
  "by_level": {
    "1": {"accuracy": 0.95, "count": 50},
    "2": {"accuracy": 0.88, "count": 30},
    "3": {"accuracy": 0.75, "count": 20}
  }
}
```

## Reproducibility

### Deterministic Execution

- **Seed-based**: All random operations use fixed seed
- **Stateless**: No persistent state across episodes
- **Tool Determinism**: Calculator uses deterministic arithmetic
- **Logging**: Complete execution logs for debugging

### Consistency Checks

- Run same task multiple times with same seed → identical results
- Run same task with different seeds → same answer (if deterministic)
- Run batch evaluation → consistent summary statistics

## Evaluation Best Practices

### For Evaluators

1. **Use Fixed Seeds**: Always specify a seed for reproducibility
2. **Run Multiple Times**: Verify consistency across runs
3. **Check Logs**: Review execution logs for quality issues
4. **Analyze Failures**: Examine failed tasks for patterns
5. **Compare Dimensions**: Look beyond accuracy to other dimensions

### For Developers

1. **Implement All Dimensions**: Ensure all metrics are computed
2. **Log Comprehensively**: Include all relevant execution details
3. **Handle Errors Gracefully**: Failures should be logged, not crash
4. **Validate Inputs**: Check task format before execution
5. **Test Edge Cases**: Verify handling of unusual inputs

## Limitations and Future Work

### Current Limitations

- **Numeric Focus**: Primarily evaluates numeric answers
- **Simple Matching**: Uses exact/partial matching (no semantic matching)
- **Limited Context**: Doesn't evaluate reasoning quality in depth
- **No Partial Credit**: Binary correctness for most metrics

### Future Enhancements

- **Semantic Matching**: Use embeddings for answer comparison
- **Partial Credit**: Award partial scores for partially correct answers
- **Reasoning Evaluation**: Deeper analysis of reasoning chains
- **Multi-modal Support**: Extend to image-based tasks
- **Adversarial Testing**: Test robustness to adversarial inputs

## References

- GAIA Benchmark: https://arxiv.org/abs/2311.12983
- AgentBeats Framework: https://rdi.berkeley.edu/agentx-agentbeats.html
- Evaluation Best Practices: See README.md and ARCHITECTURE.md
