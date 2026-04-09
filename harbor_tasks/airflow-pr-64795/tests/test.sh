#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Install pytest if not already available
pip install pytest -q 2>/dev/null || true

# Run the test_outputs.py file
cd /workspace/airflow
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Check if all tests passed
if grep -q "PASSED" /logs/verifier/pytest_output.txt && ! grep -qE "(FAILED|ERROR)" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed! Reward = 1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed. Reward = 0"
fi
