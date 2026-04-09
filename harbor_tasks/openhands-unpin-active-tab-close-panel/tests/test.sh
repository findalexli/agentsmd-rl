#!/bin/bash

# Disable errexit for proper pytest exit code capture
set +e

echo "Running test_outputs.py..."
cd /workspace/OpenHands

# Run pytest using module mode for proper exit code
python3 -m pytest /tests/test_outputs.py -v --tb=short > /logs/verifier/pytest_output.txt 2>&1
PYTEST_EXIT=$?

# Output to console
cat /logs/verifier/pytest_output.txt

# Write binary reward based on pytest exit code
if [ $PYTEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed (exit code: $PYTEST_EXIT)"
fi

cat /logs/verifier/reward.txt
exit 0
