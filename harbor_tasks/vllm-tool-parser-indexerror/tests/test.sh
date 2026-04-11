#!/bin/bash
# Test script that runs pytest and records reward

set -e

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Run pytest and capture results
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
