#!/bin/bash
set -e

# Ensure log directory exists
mkdir -p /logs/verifier

# Run Python tests with pytest
cd /workspace/playwright
python3 -m pytest /tests/test_outputs.py -v 2>&1 | tee /tmp/test_output.txt

# Check if all tests passed
if grep -q "passed" /tmp/test_output.txt && ! grep -q "failed" /tmp/test_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
    exit 1
fi
