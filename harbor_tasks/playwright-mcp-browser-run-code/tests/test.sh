#!/bin/bash
set -e

# Set up Python path
export PYTHONPATH="/tests:$PYTHONPATH"

# Create logs directory
mkdir -p /logs/verifier

# Run pytest and capture output
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

echo "Test completed. Reward written to /logs/verifier/reward.txt"
cat /logs/verifier/reward.txt
