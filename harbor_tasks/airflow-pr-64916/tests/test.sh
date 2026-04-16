#!/bin/bash
# Standard test runner for benchmark tasks
set -e

# Install pytest if not present
pip install --quiet pytest

# Run tests and capture result
cd /workspace/airflow
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_RESULT=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
