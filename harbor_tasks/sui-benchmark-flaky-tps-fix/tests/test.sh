#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Runs pytest and outputs binary reward to /logs/verifier/reward.txt

REWARD_FILE="/logs/verifier/reward.txt"

# Ensure logs directory exists
mkdir -p /logs/verifier

# Run pytest with verbose output
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$REWARD_FILE"
    echo "All tests passed. Reward: 1"
else
    echo "0" > "$REWARD_FILE"
    echo "Some tests failed. Reward: 0"
    exit 1
fi
