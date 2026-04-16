#!/bin/bash

echo "Running test suite..."

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run tests with verbose output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Get test results
PYTEST_OUTPUT=$(python3 -m pytest test_outputs.py --tb=no -q 2>&1)
echo "Test summary: $PYTEST_OUTPUT"

# Extract passed/failed counts
PASSED=$(echo "$PYTEST_OUTPUT" | grep -oP '\d+(?= passed)' || echo "0")
FAILED=$(echo "$PYTEST_OUTPUT" | grep -oP '\d+(?= failed)' || echo "0")

# Binary reward: 1 if all tests pass, 0 otherwise
if [ "$FAILED" -eq "0" ] && [ "$PASSED" -gt "0" ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed ($FAILED failed, $PASSED passed) - reward=0"
fi

cat /logs/verifier/reward.txt
