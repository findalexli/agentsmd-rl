#!/bin/bash
set -e

# Install pytest if not already installed
pip install pytest -q

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Run the tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results
# If pytest succeeded (exit code 0), reward=1, else reward=0
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
