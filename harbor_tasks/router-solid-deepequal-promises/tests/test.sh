#!/bin/bash
set -e

# Install pytest if not already available
if ! command -v pytest &> /dev/null; then
    python3 -m pip install pytest -q
fi

# Create logs directory
mkdir -p /logs/verifier

# Run the test script and capture output
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
