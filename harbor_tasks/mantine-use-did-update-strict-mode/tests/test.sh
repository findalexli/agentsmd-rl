#!/bin/bash
set -e

# Ensure log directory exists
mkdir -p /logs/verifier

# Change to the repository directory
cd /workspace/mantine/packages/@mantine/hooks

# Run pytest on test_outputs.py and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Get the actual test summary line
# Look for "passed" or "failed" in the summary line (e.g., "7 passed in 0.12s" or "4 failed, 3 passed")
TEST_SUMMARY=$(tail -5 /logs/verifier/pytest_output.txt | grep -E "(passed|failed)")

# Check if any tests failed
if echo "$TEST_SUMMARY" | grep -q "failed"; then
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
else
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
fi
