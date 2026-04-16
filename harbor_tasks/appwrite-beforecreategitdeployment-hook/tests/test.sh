#!/bin/bash
set -e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Run pytest and capture output
if pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > "$REWARD_FILE"
    echo "All tests passed - reward=1"
else
    echo "0" > "$REWARD_FILE"
    echo "Some tests failed - reward=0"
fi

cat "$REWARD_FILE"
