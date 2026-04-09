#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest pyyaml jmespath -q

# Create log directory
mkdir -p /logs/verifier

# Run tests and capture results
cd /workspace/airflow
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
