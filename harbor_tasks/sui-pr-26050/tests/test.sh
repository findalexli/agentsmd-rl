#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Run pytest on all tests and capture output
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
