#!/bin/bash
set -e

export PYTHONPATH="/workspace/prefect/src:${PYTHONPATH}"

cd /workspace/prefect

# Run the test file
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write reward based on test results
if grep -q "PASSED" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
