#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install pytest if not already installed
pip install pytest pyarrow numpy --quiet

# Set up Python path to include the lancedb python package
export PYTHONPATH=/workspace/lancedb/python/python:$PYTHONPATH

# Install lancedb from PyPI for imports (lightweight, no Rust build needed)
pip install lancedb --quiet 2>/dev/null || true

# Run the test suite and capture output
echo "Running tests..."
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "Tests passed - writing reward 1"
    echo "1" > /logs/verifier/reward.txt
else
    echo "Tests failed - writing reward 0"
    echo "0" > /logs/verifier/reward.txt
fi

echo "Test execution complete. Reward written to /logs/verifier/reward.txt"
