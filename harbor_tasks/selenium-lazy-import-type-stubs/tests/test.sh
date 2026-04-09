#!/bin/bash
set -e

# Ensure log directory exists
mkdir -p /logs/verifier

# Install pytest and CI tools if needed
pip install -q pytest mypy ruff validate-pyproject 2>/dev/null || true

# Run the test file
cd /workspace/selenium/py
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Convert to binary reward (1 if all tests pass, 0 otherwise)
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
