#!/bin/bash

# Create log directory
mkdir -p /logs/verifier

# Run pytest and capture both output and exit code
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    # All tests passed - reward = 1
    echo "1" > /logs/verifier/reward.txt
else
    # Some tests failed - reward = 0
    echo "0" > /logs/verifier/reward.txt
fi

echo ""
echo "=== Reward ==="
cat /logs/verifier/reward.txt
