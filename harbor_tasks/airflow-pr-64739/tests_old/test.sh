#!/bin/bash
# Test runner for airflow-helm-worker-extra-containers task
# This script runs pytest and writes binary reward to /logs/verifier/reward.txt

set -e

# Ensure output directory exists
mkdir -p /logs/verifier

# Install pytest if needed
pip install --quiet pytest pyyaml 2>/dev/null || true

# Run tests
cd /tests
if python -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
