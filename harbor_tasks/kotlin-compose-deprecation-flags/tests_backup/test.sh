#!/bin/bash
set -e

# Install pytest and run tests
pip install pytest -q

# Create logs directory if not exists
mkdir -p /logs/verifier

# Run tests and capture output
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
    exit 1
fi
