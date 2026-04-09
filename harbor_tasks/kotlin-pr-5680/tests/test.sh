#!/bin/bash
set -e

# Ensure log directory exists
mkdir -p /logs/verifier

# Run pytest on the test file
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
