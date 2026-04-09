#!/bin/bash
set -e

cd /workspace

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Use pre-installed virtual environment
source /workspace/venv/bin/activate

# Run pytest on the test file
if pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
