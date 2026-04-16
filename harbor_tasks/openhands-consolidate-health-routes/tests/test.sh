#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# This script runs test_outputs.py and writes binary reward to /logs/verifier/reward.txt

# Ensure log directory exists
mkdir -p /logs/verifier

# Install pytest if not already available
pip install pytest fastapi httpx starlette psutil --quiet 2>/dev/null || true

# Run tests
cd /workspace/OpenHands || true

# Set Python path
export PYTHONPATH=/workspace/OpenHands:$PYTHONPATH

# Run pytest and capture results
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "✓ All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "✗ Some tests failed - reward=0"
fi
