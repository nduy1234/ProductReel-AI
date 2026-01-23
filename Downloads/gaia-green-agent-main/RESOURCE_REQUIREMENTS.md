# Resource Requirements

This document specifies the computational, memory, and time requirements for running the GAIA Green Agent benchmark.

## Overview

The GAIA Green Agent is designed to be lightweight and efficient, with minimal resource requirements suitable for standard computing environments.

## Computational Requirements

### Minimum Requirements

- **CPU**: 1 core (2.0 GHz or higher recommended)
- **Memory**: 512 MB RAM
- **Storage**: 100 MB free space (for code and dependencies)
- **Python**: 3.8 or higher

### Recommended Requirements

- **CPU**: 2+ cores (for parallel task processing if extended)
- **Memory**: 1 GB RAM (for batch processing)
- **Storage**: 500 MB free space (for datasets and results)
- **Python**: 3.9 or higher

### Production Requirements

- **CPU**: 4+ cores (for concurrent evaluations)
- **Memory**: 2 GB RAM (for large batch processing)
- **Storage**: 1 GB+ free space (for full GAIA dataset)
- **Python**: 3.9+ (tested on 3.9, 3.10, 3.11)

## Memory Usage

### Per-Task Memory

- **Base Agent**: ~10-20 MB
- **Calculator Tool**: ~5 MB
- **Task Data**: ~1-5 MB per task (depends on task complexity)
- **Execution Logs**: ~1-10 MB per task (depends on verbosity)

### Batch Processing Memory

- **Small Batch (10 tasks)**: ~50-100 MB
- **Medium Batch (100 tasks)**: ~200-500 MB
- **Large Batch (1000 tasks)**: ~1-2 GB

### Memory Optimization

- Logs are written to disk incrementally
- No in-memory caching (stateless design)
- Garbage collection handles cleanup automatically

## Time Requirements

### Per-Task Execution Time

- **Simple Task (Level 1)**: 0.1-0.5 seconds
- **Multi-Step Task (Level 2)**: 0.3-1.0 seconds
- **Complex Task (Level 3)**: 0.5-2.0 seconds

### Batch Processing Time

- **10 tasks**: ~5-10 seconds
- **100 tasks**: ~1-2 minutes
- **1000 tasks**: ~10-20 minutes

### Time Breakdown

- **Task Loading**: < 0.01 seconds per task
- **Planning Phase**: < 0.01 seconds per task
- **Execution Phase**: 0.1-1.5 seconds per task (depends on complexity)
- **Verification Phase**: < 0.01 seconds per task
- **Result Saving**: < 0.01 seconds per task

## Storage Requirements

### Code and Dependencies

- **Base Code**: ~2 MB
- **Dependencies (minimal)**: ~5 MB (PyYAML only)
- **Dependencies (full)**: ~50-100 MB (with pandas, datasets, etc.)

### Data Storage

- **Sample Data**: ~5 KB (8 sample tasks)
- **GAIA Validation Set**: ~10-50 MB (depends on format)
- **GAIA Full Dataset**: ~100-500 MB

### Results Storage

- **Per-Task Result**: ~5-20 KB (JSON with logs)
- **Summary File**: ~10-100 KB (depends on batch size)
- **100 Tasks**: ~1-2 MB
- **1000 Tasks**: ~10-20 MB

## Docker Resource Requirements

### Container Specifications

- **Base Image**: python:3.9-slim (~150 MB)
- **With Dependencies**: ~200-300 MB
- **Runtime Memory**: 512 MB - 2 GB (depending on batch size)
- **CPU**: 1-4 cores (depending on workload)

### Docker Compose Configuration

```yaml
services:
  green-agent:
    # Resource limits (optional)
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
```

## Network Requirements

### For Hugging Face Datasets

- **Initial Download**: ~10-50 MB (one-time)
- **Per-Request**: Minimal (cached locally)
- **Bandwidth**: Standard internet connection sufficient

### For A2A Protocol (Purple Agent)

- **HTTP Server**: Minimal bandwidth
- **Request Size**: ~1-5 KB per task
- **Response Size**: ~5-20 KB per task

## Scalability Considerations

### Single Machine

- **Maximum Concurrent Tasks**: Limited by memory (typically 10-100)
- **Batch Size**: No hard limit (processes sequentially)
- **Throughput**: ~50-100 tasks per minute (depending on complexity)

### Distributed Deployment

- **Horizontal Scaling**: Can run multiple instances
- **Load Balancing**: Tasks can be distributed across instances
- **Shared Storage**: Results can be aggregated from multiple instances

## Performance Benchmarks

### Test Environment

- **CPU**: Intel Core i5-8250U (4 cores, 1.6-3.4 GHz)
- **Memory**: 8 GB RAM
- **Python**: 3.9.7
- **OS**: Linux (Ubuntu 20.04)

### Results

- **Simple Tasks**: 0.15 seconds average
- **Multi-Step Tasks**: 0.45 seconds average
- **Complex Tasks**: 0.85 seconds average
- **Memory Peak**: 120 MB for 100-task batch
- **Throughput**: ~80 tasks per minute

## Resource Monitoring

### Monitoring Tools

The agent includes logging for resource usage:

```python
# Enable detailed logging
python eval/run_agentbeats.py --log-level DEBUG --log-file execution.log
```

### Metrics Tracked

- Execution time per task
- Memory usage (if psutil available)
- Step count and tool invocations
- Error rates and retry counts

### Example Monitoring Script

```python
import psutil
import time
from eval.run_agentbeats import main

process = psutil.Process()
start_memory = process.memory_info().rss / 1024 / 1024  # MB
start_time = time.time()

# Run evaluation
main()

end_time = time.time()
end_memory = process.memory_info().rss / 1024 / 1024  # MB

print(f"Execution time: {end_time - start_time:.2f} seconds")
print(f"Memory usage: {end_memory - start_memory:.2f} MB")
```

## Optimization Tips

### For Faster Execution

1. **Use JSON Format**: Faster than Parquet for small datasets
2. **Limit Logging**: Reduce log verbosity for production runs
3. **Batch Processing**: Process multiple tasks in one run
4. **Disable Verification**: Skip detailed verification for speed (not recommended)

### For Lower Memory Usage

1. **Process Incrementally**: Don't load all tasks at once
2. **Stream Results**: Write results immediately, don't accumulate
3. **Limit Log Size**: Truncate or compress logs
4. **Use Generators**: Process tasks one at a time

### For Production Deployment

1. **Set Resource Limits**: Use Docker resource limits
2. **Monitor Usage**: Track memory and CPU usage
3. **Implement Timeouts**: Set maximum execution time per task
4. **Error Recovery**: Handle out-of-memory errors gracefully

## Troubleshooting

### Out of Memory Errors

- **Symptom**: `MemoryError` or process killed
- **Solution**: Reduce batch size, process incrementally, increase available memory

### Slow Execution

- **Symptom**: Tasks take much longer than expected
- **Solution**: Check CPU usage, reduce logging, optimize data loading

### High Storage Usage

- **Symptom**: Disk space filling up
- **Solution**: Clean old results, compress logs, use external storage

## References

- See `README.md` for installation and usage
- See `DEPLOYMENT.md` for deployment guidelines
- See `EVALUATION_METHODOLOGY.md` for evaluation details
