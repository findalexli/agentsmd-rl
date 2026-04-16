#!/bin/bash
set -e

# Standard test runner for benchmark tasks

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Install pytest if not already installed
pip install pytest -q

# Run tests and capture output
cd /workspace/dagster
if python -m pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
    echo "Tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Tests failed - reward=0"
fi
