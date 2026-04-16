#!/bin/bash
# Test runner script

# Ensure logs directory exists
mkdir -p /logs/verifier

# Run tests and capture result
cd /tests
set +e
python3 -m pytest test_outputs.py -v --tb=short > /logs/verifier/test_output.txt 2>&1
TEST_EXIT_CODE=$?
set -e

# Write binary reward based on pytest exit code
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/test_output.txt
exit 0
