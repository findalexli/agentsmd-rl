#!/bin/bash
set -e

# Install pytest
pip install pytest -q

# Create log directory
mkdir -p /logs/verifier

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Calculate reward (1 if all tests pass, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward: 1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward: 0"
fi
