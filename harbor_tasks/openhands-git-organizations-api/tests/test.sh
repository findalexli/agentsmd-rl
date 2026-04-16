#!/bin/bash
set -e

# Create log directory if not exists
mkdir -p /logs/verifier

# Copy tests to workspace (writable location) and run with poetry env
cp /tests/test_outputs.py /workspace/test_outputs.py

# Run using the poetry environment from OpenHands
cd /workspace/OpenHands
poetry run python3 -m pytest /workspace/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
