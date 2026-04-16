#!/bin/bash
set -e

# Ensure log directory exists
mkdir -p /logs/verifier

# Run pytest tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward
if python3 -m pytest test_outputs.py -q 2>/dev/null | grep -q "passed"; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
