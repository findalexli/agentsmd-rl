#!/bin/bash
# Test runner for apache/superset PR #39109 benchmark task
# Runs pytest on test_outputs.py and writes binary reward

set -e

cd /workspace/superset

# Install pytest if not present
pip install --quiet pytest 2>/dev/null || true

# Run tests and capture result
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
