#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Runs test_outputs.py using system pytest

# Create logs directory
mkdir -p /logs/verifier

# Run tests with JUnit XML output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
    --junitxml=/logs/verifier/results.xml \
    2>&1 | tee /logs/verifier/pytest.log

# Determine reward based on test results
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    # All tests passed - write reward=1
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed. Reward=1"
else
    # Some tests failed - write reward=0
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed. Reward=0"
fi

exit 0
