#!/bin/bash
set -e

REWARD_LOG="/logs/verifier/reward.txt"
TEST_DIR="/tests"

# Create the logs directory
mkdir -p /logs/verifier

# Run pytest on test_outputs.py
cd /workspace/electron

if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$REWARD_LOG"
    echo "All tests passed!"
else
    echo "0" > "$REWARD_LOG"
    echo "Some tests failed."
fi
