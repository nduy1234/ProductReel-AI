# Deployment Guide

## Pre-Deployment Checklist

- [x] All code implemented and tested
- [x] Test suite passing (100%)
- [x] Documentation complete
- [x] Configuration files ready
- [x] Sample data included

## Installation Steps

### 1. Environment Setup

```bash
# Ensure Python 3.8+ is installed
python --version

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Minimum required
pip install PyYAML

# Or install all dependencies
pip install -r requirements.txt

# Optional: For Hugging Face datasets
pip install datasets

# Optional: For Parquet files
pip install pandas pyarrow
```

### 3. Verify Installation

```bash
# Test basic functionality
python example_usage.py

# Run test suite
python test_multi_step.py
```

## Deployment Options

### Option 1: Local Execution

Run evaluations locally with sample or real GAIA data:

```bash
python eval/run_agentbeats.py \
  --config configs/gaia_agent.yaml \
  --data-source data/sample_gaia_tasks.json \
  --data-format json \
  --max-tasks 10
```

### Option 2: AgentBeats Platform

1. **Package as Docker Image** (if required by AgentBeats):
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["python", "eval/run_agentbeats.py", "--config", "configs/gaia_agent.yaml"]
   ```

2. **Register with AgentBeats**:
   - Follow AgentBeats documentation for agent registration
   - Provide agent endpoint or Docker image
   - Configure task routing

3. **Submit Tasks**:
   - Use AgentBeats API or CLI
   - Tasks will be routed to this Green Agent
   - Results returned in AgentBeats format

### Option 3: Standalone Service

Deploy as a standalone service with API endpoint:

```python
# Example Flask/FastAPI wrapper (not included, but can be added)
from flask import Flask, request, jsonify
from agent.agent import GAIAAgent
from tasks.gaia_task import GAIATask

app = Flask(__name__)
agent = GAIAAgent(seed=42)

@app.route('/execute', methods=['POST'])
def execute_task():
    task_data = request.json
    task = GAIATask.from_gaia(task_data)
    result = agent.execute(task.prompt, task_id=task.task_id)
    response = GAIATask.to_agentbeats_response(result)
    return jsonify(response)
```

## Configuration

### Environment Variables

Set these if needed:
- `GAIA_DATA_PATH`: Path to GAIA dataset
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `OUTPUT_DIR`: Results output directory

### Config File

Edit `configs/gaia_agent.yaml`:
- Agent seed for reproducibility
- Retry limits
- Calculator precision
- Data source paths
- Output directories

## Monitoring

### Logs

Logs are written in JSON format:
- Execution logs: Per-task JSON files
- Summary logs: `summary.json` in output directory
- Console logs: Structured output

### Metrics

Track:
- Task completion rate
- Accuracy (correct/incorrect)
- Average execution time
- Tool invocation counts
- Verification pass rates

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies installed
   - Check Python path
   - Verify `__init__.py` files exist

2. **Data Loading Failures**
   - Verify file paths
   - Check file permissions
   - Ensure correct format specified

3. **Calculator Errors**
   - Check expression syntax
   - Verify number formats
   - Review error messages in logs

4. **AgentBeats Integration**
   - Verify A2A protocol compliance
   - Check task format
   - Review response structure

## Performance Considerations

- **Batch Processing**: Process multiple tasks sequentially
- **Caching**: Consider caching common computations
- **Parallelization**: Can be extended for parallel execution
- **Resource Limits**: Monitor memory and CPU usage

## Security

- Calculator uses safe parser (no eval() vulnerabilities)
- Input sanitization in place
- No code execution from user input
- Deterministic behavior prevents injection

## Maintenance

### Regular Tasks
- Update dependencies
- Review and extend test cases
- Monitor performance metrics
- Update documentation

### Version Updates
- Check CHANGELOG.md for changes
- Review breaking changes
- Update configuration if needed
- Re-run test suite

## Support

For issues or questions:
1. Check README.md for usage
2. Review ARCHITECTURE.md for design details
3. Examine test cases for examples
4. Check logs for error details

---

**Ready for deployment!** 🚀
