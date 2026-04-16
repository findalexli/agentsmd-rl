#!/bin/bash
# Test runner for benchmark task
# Runs test_outputs.py and writes binary reward (0 or 1) to /logs/verifier/reward.txt

set -e

# Ensure output directory exists
mkdir -p /logs/verifier

# Install pytest if not already installed
pip install --quiet pytest pytest-timeout 2>/dev/null || true

# Run the tests
cd /workspace/superset

if python -m pytest /tests/test_outputs.py -v --tb=short --timeout=300; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
