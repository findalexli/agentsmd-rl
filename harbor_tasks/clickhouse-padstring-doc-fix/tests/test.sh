#!/bin/bash
set -e

# Install pytest if needed
pip3 install -q pytest 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run pytest and capture output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "PASS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAIL: Some tests failed"
fi

exit $EXIT_CODE
