#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Runs test_outputs.py via pytest and writes binary reward to /logs/verifier/reward.txt

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Run pytest on the test file
cd /workspace/mantine
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$REWARD_FILE"
    echo "All tests passed - reward=1"
else
    echo "0" > "$REWARD_FILE"
    echo "Some tests failed - reward=0"
fi

cat "$REWARD_FILE"
