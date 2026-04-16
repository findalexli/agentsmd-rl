#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Installs pytest, runs test_outputs.py, and writes binary reward

REWARD_FILE="/logs/verifier/reward.txt"
TEST_FILE="/tests/test_outputs.py"

# Ensure logs directory exists
mkdir -p /logs/verifier

# Install pytest if not available
pip install pytest -q 2>/dev/null || true

# Run pytest and capture result
if python3 "$TEST_FILE"; then
    echo "1" > "$REWARD_FILE"
    echo "All tests passed - reward=1"
else
    echo "0" > "$REWARD_FILE"
    echo "Some tests failed - reward=0"
fi
