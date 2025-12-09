#!/bin/bash
#
# Setup script for OpenCUA-7B API Server
#
# This script creates a new conda environment and installs all dependencies
#

set -e

echo "========================================"
echo "OpenCUA-7B API Server Setup"
echo "========================================"
echo

# Create conda environment
echo "Creating conda environment 'opencua_inference'..."
conda create -n opencua_inference python=3.10 -y

# Install dependencies
echo
echo "Installing dependencies..."
conda run -n opencua_inference pip install \
    transformers==4.53.0 \
    torch==2.8.0 \
    pillow==11.3.0 \
    tiktoken==0.11.0 \
    blobfile==3.0.0 \
    accelerate==1.10.0 \
    fastapi \
    uvicorn \
    openai \
    requests

echo
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "To start the server:"
echo "  ./models/opencua/start_server.sh [PORT]"
echo
echo "Default port: 8000"
echo "Example: ./models/opencua/start_server.sh 8001"
echo
