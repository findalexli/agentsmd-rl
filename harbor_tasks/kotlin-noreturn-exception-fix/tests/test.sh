#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Runs pytest and writes binary reward to /logs/verifier/reward.txt

pip install pytest --quiet 2>/dev/null

# Run tests and capture result
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "Tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Tests failed - reward=0"
fi
