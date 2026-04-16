#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Run pytest with verbose output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Extract pass/fail counts
PASSED=$(grep -oP '\d+ passed' /logs/verifier/pytest_output.txt | grep -oP '\d+' || echo "0")
FAILED=$(grep -oP '\d+ failed' /logs/verifier/pytest_output.txt | grep -oP '\d+' || echo "0")

# Calculate binary reward (1 if all tests pass, 0 otherwise)
if [ "$PASSED" -gt 0 ] && [ "$FAILED" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
