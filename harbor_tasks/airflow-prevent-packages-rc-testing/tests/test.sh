#!/bin/bash

# Install pytest if not already installed
pip install --quiet pytest 2>/dev/null || true

# Run the tests
cd /workspace/airflow
if pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
