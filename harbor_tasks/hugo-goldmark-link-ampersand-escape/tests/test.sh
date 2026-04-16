#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
if pytest -v /tests/test_outputs.py 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi
