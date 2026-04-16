#!/bin/bash
set -e

# Ensure log directory exists
mkdir -p /logs/verifier

# Change to tests directory to find test_outputs.py
cd /tests

# Run pytest with verbose output, capturing results
python3 -m pytest test_outputs.py -v --tb=short 2>&1 || true

# Check test results and write reward
# If all tests pass, pytest exits with 0
if python3 -m pytest test_outputs.py -v --tb=short --co -q 2>&1 | grep -q "no tests ran"; then
    echo "0" > /logs/verifier/reward.txt
    echo "ERROR: No tests found"
    exit 1
fi

# Run the actual tests and capture exit code
if python3 -m pytest test_outputs.py --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
