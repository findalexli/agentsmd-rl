#!/bin/bash
set -e

# Standardized test runner for Harbor tasks
# Runs pytest on test_outputs.py and writes reward to /logs/verifier/reward.txt

mkdir -p /logs/verifier

# Run pytest and capture output
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "PASS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAIL: Some tests failed"
fi
