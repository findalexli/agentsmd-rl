#!/bin/bash
set -e

REWARD_FILE="/logs/verifier/reward.txt"

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install --break-system-packages pytest 2>/dev/null || pip3 install pytest
fi

# Run tests and capture results
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$REWARD_FILE"
    echo "All tests passed - reward=1"
else
    echo "0" > "$REWARD_FILE"
    echo "Tests failed - reward=0"
fi
