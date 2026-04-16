#!/bin/bash
set -e

# Standard Harbor test runner
# Runs pytest and writes reward to /logs/verifier/reward.txt

cd /tests

# Run pytest and capture results
if python3 -m pytest test_outputs.py -v 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward 1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward 0"
fi
