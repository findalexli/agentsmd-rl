#!/bin/bash
set -e

# Create logs directory if needed
mkdir -p /logs/verifier

# Run pytest on test_outputs.py
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests pass, 0 otherwise
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1" >&2
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0" >&2
fi

cat /logs/verifier/reward.txt
