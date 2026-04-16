#!/bin/bash

# Create log directory
mkdir -p /logs/verifier

# Run tests and capture output (don't exit on failure)
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log
TEST_EXIT=${PIPESTATUS[0]}

if [ $TEST_EXIT -eq 0 ]; then
    # All tests passed - reward=1
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    # Some tests failed - reward=0
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
