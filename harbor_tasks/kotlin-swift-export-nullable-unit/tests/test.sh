#!/bin/bash
set -e

# Install pytest if not present
pip install pytest -q

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture result
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
