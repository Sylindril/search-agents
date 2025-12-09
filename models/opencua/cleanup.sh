#!/bin/bash
#
# Cleanup script for OpenCUA-7B API Server
#
# This script:
# - Kills all running server processes
# - Clears GPU memory
# - Cleans up temporary files
#

echo "========================================"
echo "OpenCUA-7B Server Cleanup"
echo "========================================"
echo

# Kill server processes
echo "Stopping server processes..."
pkill -9 -f "models/opencua/server.py" 2>/dev/null && echo "✓ Server processes killed" || echo "  (No server processes found)"

# Kill conda run processes that might be lingering
pkill -9 -f "conda run.*opencua" 2>/dev/null && echo "✓ Conda processes cleaned" || echo "  (No conda processes found)"

# Wait for processes to fully terminate
sleep 2

# Check GPU status
echo
echo "Checking GPU status..."
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader 2>/dev/null | grep -i python && {
    echo "⚠ Warning: Python processes still using GPU"
    echo "  Run: nvidia-smi to see details"
} || echo "✓ No Python processes on GPU"

# Show current GPU memory
echo
echo "Current GPU memory usage:"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader

# Clean up any zombie processes
echo
echo "Cleaning up zombie processes..."
ps aux | grep defunct | grep -v grep && {
    echo "⚠ Warning: Zombie processes found"
    echo "  They will be cleaned up by the system"
} || echo "✓ No zombie processes"

# Optional: Clear Python cache (uncomment if needed)
# echo
# echo "Clearing Python cache..."
# find /home/adityaku/search-agents/models/opencua -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
# echo "✓ Python cache cleared"

echo
echo "========================================"
echo "Cleanup Complete!"
echo "========================================"
echo
echo "GPU should be free now. Wait 5-10 seconds before restarting."
echo
