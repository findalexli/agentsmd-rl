#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Runs pytest and outputs binary reward to /logs/verifier/reward

mkdir -p /logs/verifier

# Install pytest
pip install pytest -q

# Run tests
cd /tests
if pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed!"
    exit 1
fi
