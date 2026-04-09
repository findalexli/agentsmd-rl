#!/bin/bash
set -e

cd /workspace/task/tests

# Install pytest if not present
pip install pytest -q

# Run the test file
python -m pytest test_outputs.py -v

# Write binary reward based on test results
if [ $? -eq 0 ]; then
    echo "PASS" > /logs/verifier/reward.txt
    exit 0
else
    echo "FAIL" > /logs/verifier/reward.txt
    exit 1
fi
