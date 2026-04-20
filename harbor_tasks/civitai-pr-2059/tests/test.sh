#!/bin/bash

# Run the tests
cd /workspace
python -m pytest /tests/test_outputs.py -v --tb=short --no-header
TEST_RESULT=$?

# Write reward (0 or 1) to /logs/verifier/reward.txt
# This is automatically picked up by the harness
if [ $TEST_RESULT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi