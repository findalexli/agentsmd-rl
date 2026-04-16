#!/bin/bash
set -e

# Run tests and capture exit code
set +e
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt
TEST_EXIT_CODE=${PIPESTATUS[0]}
set -e

# Write binary reward based on test exit code
if [ "$TEST_EXIT_CODE" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi