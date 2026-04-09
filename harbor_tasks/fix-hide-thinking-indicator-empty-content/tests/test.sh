#!/bin/bash
set -e

echo "Installing pytest..."
pip3 install pytest --quiet

echo "Running tests..."
cd /workspace/task
cd tests
python3 -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (0 or 1 based on pass/fail)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "PASS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAIL: Some tests failed"
fi
