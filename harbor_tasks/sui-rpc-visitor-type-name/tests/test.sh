#!/bin/bash
set -e

# Create logs directory if needed
mkdir -p /logs/verifier

# Run pytest and capture output
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
    exit 1
fi
