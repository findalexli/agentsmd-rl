#!/bin/bash
set -e

# Run pytest and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Check if all tests passed
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
