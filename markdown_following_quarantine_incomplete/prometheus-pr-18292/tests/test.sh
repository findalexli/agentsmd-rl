#!/bin/bash
set -e

# Install dependencies if needed
pip3 install pytest --quiet 2>/dev/null || true

# Run pytest and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Extract test results and write reward
# Reward is 1 if all tests pass, 0 otherwise
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
