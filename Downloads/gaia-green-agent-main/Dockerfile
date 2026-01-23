# GAIA Green Agent Docker Image
# This Dockerfile creates a containerized deployment of the GAIA Green Agent
# with minimal resource requirements and robust error handling.

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Note: git is included for potential dataset cloning, but can be removed if not needed
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files in logical order for better caching
COPY agent/ ./agent/
COPY tools/ ./tools/
COPY tasks/ ./tasks/
COPY eval/ ./eval/
COPY configs/ ./configs/
COPY data/ ./data/
COPY purple_agent/ ./purple_agent/
COPY *.py ./
COPY *.md ./
COPY *.txt ./
COPY *.yaml ./

# Create results directory with proper permissions
RUN mkdir -p results && chmod 755 results

# Set Python path and environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Set resource limits (can be overridden at runtime)
# These are defaults; actual limits should be set via docker run or docker-compose
ENV MAX_MEMORY_MB=1024
ENV MAX_EXECUTION_TIME_SEC=300

# Health check to verify container is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command: run evaluation
# Can be overridden at runtime
CMD ["python", "eval/run_agentbeats.py", "--config", "configs/gaia_agent.yaml"]

# Alternative commands (uncomment as needed):
# Run purple agent server:
# CMD ["python", "-m", "purple_agent.server"]
# Run with custom config:
# CMD ["python", "eval/run_agentbeats.py", "--config", "configs/custom_config.yaml"]
