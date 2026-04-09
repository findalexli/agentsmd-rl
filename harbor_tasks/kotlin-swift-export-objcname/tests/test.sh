#!/bin/bash
set -e

# Install pytest
pip install pytest --quiet

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Check if tests passed
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

echo "Reward written: $(cat /logs/verifier/reward.txt)"
