#!/bin/bash
set -e

# Ensure pytest is available
if ! command -v pytest &> /dev/null; then
    pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest
fi

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
cd /tests
if pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi
