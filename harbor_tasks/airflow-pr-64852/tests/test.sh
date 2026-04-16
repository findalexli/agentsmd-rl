#!/bin/bash
# Standard test runner for benchmark tasks

# Install pytest if not available
pip install --quiet pytest pytest-timeout 2>/dev/null || true

# Run the tests and capture exit code
cd /workspace/airflow
python -m pytest /tests/test_outputs.py -v --tb=short --timeout=300
RESULT=$?

# Write reward based on test results
if [ $RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
