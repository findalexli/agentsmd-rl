#!/bin/bash
set -e

# Install pytest if not already available
pip install pytest msgspec structlog --quiet

# Run the test file and output structured results
cd /workspace/airflow
python -m pytest /workspace/task/tests/test_outputs.py -v --tb=short 2>&1 | tee /tmp/test_output.txt

# Write binary reward file based on test results
if grep -q "passed" /tmp/test_output.txt && ! grep -q "FAILED" /tmp/test_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
    exit 1
fi
