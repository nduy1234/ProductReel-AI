# Abstract: GAIA Green Agent for AgentBeats

## Overview

This project implements a **Green Agent** that ports the GAIA benchmark (math subset) into an end-to-end AgentBeats-compatible evaluation system. The agent converts static GAIA math problems into executable agent workflows, demonstrating tool-grounded reasoning through a structured Plan → Act → Verify → Answer loop.

## Task Description

The Green Agent evaluates mathematical problem-solving capabilities by:

1. **Loading GAIA Tasks**: Converts GAIA benchmark problems (JSON, JSONL, Parquet, or Hugging Face formats) into agent-executable episodes
2. **Task Decomposition**: Analyzes problems to identify required mathematical operations and execution order
3. **Tool-Grounded Execution**: Performs computations using explicit tool invocations (deterministic calculator)
4. **Verification**: Validates intermediate and final results at multiple levels
5. **Answer Generation**: Produces concise, structured answers without hidden chain-of-thought

## Key Features

- **Deterministic Execution**: Reproducible results with fixed seeds
- **Stateless Design**: No persistent state across episodes (except logs)
- **Multi-Step Problem Handling**: Supports sequential operations (e.g., "X, then Y")
- **AgentBeats Compatibility**: Full A2A protocol compliance for task management and evaluation
- **Comprehensive Logging**: Machine-readable JSON logs for all execution phases
- **Batch Evaluation**: Processes multiple tasks with summary statistics

## Architecture

The agent implements a structured execution loop:

- **Planning Phase**: Parses problems and creates ordered execution steps
- **Action Phase**: Invokes mathematical tools (calculator) for computations
- **Verification Phase**: Checks step results and final answers with retry logic
- **Answer Phase**: Emits normalized, structured final answers

## Evaluation Capabilities

The Green Agent can evaluate:
- Single-step arithmetic problems
- Multi-step sequential operations
- Problems requiring intermediate result chaining
- Tasks from GAIA benchmark (math subset)

## Technical Implementation

- **Language**: Python 3.8+
- **Tools**: Custom calculator with safe parser (no eval vulnerabilities)
- **Data Formats**: Supports JSON, JSONL, Parquet, and Hugging Face datasets
- **Testing**: Comprehensive test suite with 100% pass rate
- **Documentation**: Complete guides for usage, architecture, and deployment

## Submission Components

1. **Green Agent**: Complete implementation with Plan→Act→Verify→Answer loop
2. **Baseline Purple Agent**: Simple A2A-compatible agent demonstrating evaluation workflow
3. **Docker Image**: Containerized deployment for reproducible execution
4. **Documentation**: README, architecture docs, and deployment guides

## Use Cases

- Benchmarking mathematical reasoning capabilities
- Evaluating tool-using agents on GAIA tasks
- Demonstrating AgentBeats Green Agent implementation patterns
- Research on verifiable, tool-grounded agent execution
