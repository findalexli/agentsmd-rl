#!/bin/bash
set -e

# Setup logging
mkdir -p /logs/verifier
LOG_FILE="/logs/verifier/test_output.log"
REWARD_FILE="/logs/verifier/reward.txt"

# Run pytest and capture result
if pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee "$LOG_FILE"; then
    # Check if any tests actually failed (pytest returns 0 only if all pass)
    if grep -q "FAILED" "$LOG_FILE"; then
        echo "0" > "$REWARD_FILE"
        echo "FAILURE: Some tests failed"
    elif grep -q "passed" "$LOG_FILE"; then
        echo "1" > "$REWARD_FILE"
        echo "SUCCESS: All tests passed"
    else
        echo "0" > "$REWARD_FILE"
        echo "FAILURE: No test results found"
    fi
else
    # pytest command failed
    echo "0" > "$REWARD_FILE"
    echo "FAILURE: pytest command failed or tests failed"
fi

cat "$REWARD_FILE"
