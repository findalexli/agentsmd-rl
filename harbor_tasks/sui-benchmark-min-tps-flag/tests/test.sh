#!/bin/bash

# Standard test runner for benchmark tasks
# This script runs pytest on test_outputs.py and records the reward

# Setup
mkdir -p /logs/verifier

# Run pytest and capture results (don't exit on failure)
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log || true

# Check if all tests passed
if grep -q "passed" /logs/verifier/pytest_output.log && ! grep -q "FAILED" /logs/verifier/pytest_output.log; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0"
fi

# Return success even if tests fail (the reward file records the result)
exit 0
