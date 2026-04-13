#!/bin/bash
# Boilerplate test runner - executes pytest and records reward

set -e

cd /workspace/calculator

# Run pytest and capture results
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0"
fi
