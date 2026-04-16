#!/bin/bash

# Install pytest if not available
pip install --quiet pytest pyyaml

# Run tests and capture exit code
cd /workspace/airflow
if python -m pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
