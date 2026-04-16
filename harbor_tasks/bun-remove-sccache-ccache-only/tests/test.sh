#!/bin/bash
set -e

# Write reward to the shared log directory
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

cd /workspace/bun

# Run pytest and capture result
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$REWARD_FILE"
    echo "All tests passed - reward=1"
else
    echo "0" > "$REWARD_FILE"
    echo "Some tests failed - reward=0"
    exit 0  # Don't fail the container, just record 0
fi
