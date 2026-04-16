#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest -q 2>/dev/null || true

# Run tests and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results - check if any failures occurred
if grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "0" > /logs/verifier/reward.txt
else
    echo "1" > /logs/verifier/reward.txt
fi
