#!/bin/bash
set -e

# Install pytest if not present
pip install pytest pytest-mock -q

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
    exit 0  # Don't fail the container, just record 0 reward
fi
