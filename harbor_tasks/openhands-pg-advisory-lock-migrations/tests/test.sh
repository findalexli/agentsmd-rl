#!/bin/bash
set -e

# Install pytest and run tests
pip install pytest -q

# Run pytest and capture results
cd /workspace/OpenHands
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
