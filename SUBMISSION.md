# Submission Package: GAIA Green Agent for AgentBeats

## Abstract

See [ABSTRACT.md](ABSTRACT.md) for the complete abstract describing the Green Agent's evaluation capabilities.

## Public GitHub Repository

**Repository**: https://github.com/nduy1234/gaia-green-agent

**Contents**:
- Complete source code for Green Agent
- Baseline Purple Agent implementation
- Docker configuration
- Comprehensive documentation
- Test suite and examples

**README**: See [README.md](README.md) for complete usage instructions.

## Baseline Purple Agent

The baseline purple agent demonstrates how the Green Agent evaluates participant agents:

**Location**: `purple_agent/`

**Components**:
- `purple_agent.py`: A2A-compatible participant agent
- `server.py`: HTTP server implementing A2A protocol endpoint

**Usage**:
```bash
# Run as standalone server
python -m purple_agent.server

# Or via Docker
docker run -p 8000:8000 gaia-green-agent:latest python -m purple_agent.server
```

**A2A Endpoint**: `http://localhost:8000/a2a/task`

The purple agent can:
- Accept tasks via A2A protocol (POST /a2a/task)
- Process tasks (delegates to Green Agent or uses simple logic)
- Return responses in A2A format
- Serve as a baseline for evaluation demonstrations

## Docker Image

### Build

```bash
docker build -t gaia-green-agent:latest .
```

Or use the provided scripts:
- `build_docker.sh` (Linux/Mac)
- `build_docker.bat` (Windows)

### Run Green Agent

```bash
docker run -v $(pwd)/results:/app/results gaia-green-agent:latest
```

### Run Purple Agent

```bash
docker run -p 8000:8000 gaia-green-agent:latest python -m purple_agent.server
```

### Docker Compose

```bash
docker-compose up
```

Starts both Green and Purple agents.

### Image Features

- Python 3.9-slim base
- All dependencies pre-installed
- Ready to run end-to-end
- No manual intervention required
- Results saved to mounted volume

## Verification

### Test Green Agent

```bash
python example_usage.py
python test_multi_step.py
```

### Test Purple Agent

```bash
# Start server
python -m purple_agent.server

# In another terminal, test endpoint
curl -X POST http://localhost:8000/a2a/task \
  -H "Content-Type: application/json" \
  -d '{"task_id": "test_1", "task_type": "gaia_math", "prompt": "What is 2 + 2?", "metadata": {}}'
```

### Test Docker

```bash
# Build
docker build -t gaia-green-agent:latest .

# Run evaluation
docker run -v $(pwd)/results:/app/results gaia-green-agent:latest \
  python eval/run_agentbeats.py --config configs/gaia_agent.yaml --max-tasks 3
```

## File Structure

```
gaia-green-agent/
├── agent/              # Green Agent core
│   ├── agent.py       # Plan→Act→Verify→Answer
│   ├── planner.py      # Task decomposition
│   └── verifier.py     # Answer verification
├── tools/              # Tools
│   └── calculator.py   # Math calculator
├── tasks/              # Task management
│   ├── gaia_loader.py  # GAIA data loader
│   └── gaia_task.py    # AgentBeats wrapper
├── eval/               # Evaluation
│   └── run_agentbeats.py
├── purple_agent/       # Baseline Purple Agent
│   ├── purple_agent.py # A2A-compatible agent
│   └── server.py       # HTTP server
├── configs/            # Configuration
├── data/               # Sample data
├── Dockerfile          # Docker image
├── docker-compose.yml  # Multi-container setup
├── requirements.txt    # Dependencies
├── README.md           # Main documentation
└── ABSTRACT.md         # Abstract
```

## Quick Start

1. **Clone repository**:
   ```bash
   git clone https://github.com/nduy1234/gaia-green-agent.git
   cd gaia-green-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run evaluation**:
   ```bash
   python eval/run_agentbeats.py --config configs/gaia_agent.yaml --max-tasks 3
   ```

4. **Or use Docker**:
   ```bash
   docker build -t gaia-green-agent:latest .
   docker run -v $(pwd)/results:/app/results gaia-green-agent:latest
   ```

## Requirements Compliance

- Abstract: See [ABSTRACT.md](ABSTRACT.md)
- Public GitHub: https://github.com/nduy1234/gaia-green-agent
- Baseline Purple Agent: `purple_agent/` directory
- Docker Image: `Dockerfile` and build scripts provided

All submission requirements are met.
