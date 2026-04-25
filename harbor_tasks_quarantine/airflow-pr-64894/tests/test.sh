#!/bin/bash
# Standard test runner for benchmark task

# Install pytest if not already installed
pip install --quiet pytest

# Run the tests and capture exit code
cd /workspace/airflow
python -m pytest /tests/test_outputs.py -v --tb=short
TEST_EXIT_CODE=$?

# Write reward based on test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_EXIT_CODE
