#!/bin/bash
#
# Start OpenCUA-7B API Server
#
# Usage:
#   ./start_server.sh [PORT] [CACHE_DIR]
#
# Example:
#   ./start_server.sh 8000 /data/models/huggingface
#   ./start_server.sh 8000  # Use default cache
#

PORT=${1:-8000}
CACHE_DIR=${2:-"/data/user_data/adityaku/hf_cache"}
MODEL="xlangai/OpenCUA-7B"

echo "Starting OpenCUA-7B API Server..."
echo "Port: $PORT"
echo "Cache: $CACHE_DIR"
echo "Model: $MODEL"
echo

# Build command
CMD="conda run -n opencua_inference python models/opencua/server.py --port $PORT --model $MODEL --cache-dir $CACHE_DIR"

# Run server
echo "Command: $CMD"
echo
exec $CMD
