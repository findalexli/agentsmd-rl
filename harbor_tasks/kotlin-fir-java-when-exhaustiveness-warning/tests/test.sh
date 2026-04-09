#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q 2>/dev/null || pip3 install pytest -q 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
