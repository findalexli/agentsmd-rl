#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Run pytest and capture results
cd /workspace/OpenHands
if python3 -m pytest /tests/test_outputs.py -v --tb=short > /tmp/pytest_output.txt 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

# Show test output for debugging
cat /tmp/pytest_output.txt

echo "Reward written to /logs/verifier/reward.txt"
cat /logs/verifier/reward.txt
