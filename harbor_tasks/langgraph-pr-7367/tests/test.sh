#!/bin/bash
set -e

LOGS_DIR="/logs/verifier"
mkdir -p "$LOGS_DIR"

REWARD_FILE="$LOGS_DIR/reward.txt"
OUTPUT_FILE="$LOGS_DIR/test_output.txt"

# Run pytest and capture output
if python -m pytest /tests/test_outputs.py -v --tb=short > "$OUTPUT_FILE" 2>&1; then
    echo "1" > "$REWARD_FILE"
    echo "All tests passed!"
else
    echo "0" > "$REWARD_FILE"
    echo "Some tests failed."
fi

cat "$OUTPUT_FILE"
