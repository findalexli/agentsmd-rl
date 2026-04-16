#!/bin/bash

# Standardized test runner for benchmark tasks
# This script is called by the verifier to run test_outputs.py

# Set up logging
mkdir -p /logs/verifier
REWARD_FILE="/logs/verifier/reward.txt"
LOG_FILE="/logs/verifier/test_output.log"

# Run pytest on test_outputs.py and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee "$LOG_FILE"
PYTEST_EXIT=${PIPESTATUS[0]}

if [ $PYTEST_EXIT -eq 0 ]; then
    # All tests passed
    echo "1" > "$REWARD_FILE"
    echo "SUCCESS: All tests passed. Reward = 1"
else
    # Some tests failed
    echo "0" > "$REWARD_FILE"
    echo "FAILURE: Some tests failed. Reward = 0"
fi

# Return 0 regardless of test results - the reward file contains the signal
exit 0
