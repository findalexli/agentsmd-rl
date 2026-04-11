#!/bin/bash
# Test runner for Airflow Helm Chart tests

set -e

REPO="/workspace/airflow"

# Ensure logs directory exists
mkdir -p /logs/verifier

echo "Running tests in: $REPO"
cd "$REPO"

# Run pytest on the test_outputs.py file
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 || {
    echo "Tests failed"
    echo "0" > /logs/verifier/reward.txt
    exit 1
}

# If we get here, all tests passed
echo "1" > /logs/verifier/reward.txt
echo "All tests passed!"
exit 0
