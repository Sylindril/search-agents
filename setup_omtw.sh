#!/bin/bash
# Quick setup script for OMTW on search-agents
# Usage: bash setup_omtw.sh

set -e

echo "=== OMTW Setup for search-agents ==="

# Check if in correct directory
if [ ! -f "run.py" ]; then
    echo "ERROR: Run this script from the search-agents directory"
    exit 1
fi

# Check for conda
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Please install conda first."
    exit 1
fi

echo "[1/6] Creating conda environment..."
conda create -n search-agents python=3.10 -y
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate search-agents

echo "[2/6] Installing base requirements..."
pip install -r requirements.txt
playwright install
pip install -e .

echo "[3/6] Fixing package versions..."
pip install httpx==0.25.0 openai==1.3.5
pip install torch --upgrade
pip install transformers --upgrade

echo "[4/6] Setting up OMTW config files..."
mkdir -p config_files/omtw

# Check if ExACT configs exist, otherwise create sample
if [ -d "../ExACT/configs/omtw/test_omtw" ]; then
    cp ../ExACT/configs/omtw/test_omtw/*.json config_files/omtw/
    echo "Copied OMTW configs from ExACT"
else
    echo "WARNING: ExACT configs not found. You'll need to copy them manually."
    echo "cp /path/to/ExACT/configs/omtw/test_omtw/*.json config_files/omtw/"
fi

echo "[5/6] Making run script executable..."
chmod +x scripts/run_omtw_search.sh

echo "[6/6] Checking for API key..."
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo "Found .env file"
    else
        echo "WARNING: OPENAI_API_KEY not set and no .env file found"
        echo "Create .env with: echo 'OPENAI_API_KEY=sk-your-key' > .env"
    fi
else
    echo "OPENAI_API_KEY is set"
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To run:"
echo "  conda activate search-agents"
echo "  ./scripts/run_omtw_search.sh"
echo ""
echo "First run will download BLIP2 model (~15GB)"

