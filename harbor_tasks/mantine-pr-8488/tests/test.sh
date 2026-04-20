#!/bin/bash

cd /workspace

# Install pytest if not already installed
pip install pytest==8.3.4 pytest-timeout==2.3.1 -q

# Run the tests
pytest /tests/test_outputs.py -v --tb=short
TEST_RESULT=$?

# Write reward based on test result
if [ $TEST_RESULT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi