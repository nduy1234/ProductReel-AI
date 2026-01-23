#!/bin/bash
# Build script for GAIA Green Agent Docker image

set -e

echo "Building GAIA Green Agent Docker image..."

# Build the image
docker build -t gaia-green-agent:latest .

echo "Build complete!"
echo ""
echo "To run the Green Agent:"
echo "  docker run -v \$(pwd)/results:/app/results gaia-green-agent:latest"
echo ""
echo "To run the Purple Agent server:"
echo "  docker run -p 8000:8000 gaia-green-agent:latest python -m purple_agent.server"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose up"
