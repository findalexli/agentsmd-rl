#!/bin/bash
set -e

# Install pytest if not present
pip install pytest --quiet

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
# Don't exit on failure - we need to write the reward
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
