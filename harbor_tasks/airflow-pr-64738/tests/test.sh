#!/bin/bash

# Install pytest if not present
pip install --quiet pytest pytest-timeout 2>/dev/null || true

# Ensure reward directory exists
mkdir -p /logs/verifier

# Run the tests
cd /workspace/airflow
python -m pytest /tests/test_outputs.py -v --tb=short --timeout=300
TEST_RESULT=$?

# Write reward based on test results
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
