#!/bin/bash
set -e

# Run pytest and capture exit code
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 || true

# Determine reward based on test results
# Reward is 1 if all tests pass, 0 otherwise
REWARD_FILE=/logs/verifier/reward.txt
mkdir -p /logs/verifier

# Run pytest again to check actual pass/fail status
if python3 -m pytest test_outputs.py --tb=no -q 2>&1 | grep -q "passed"; then
    # Check if all tests passed (no failures)
    if ! python3 -m pytest test_outputs.py --tb=no -q 2>&1 | grep -q "failed"; then
        echo "1" > "$REWARD_FILE"
        echo "All tests passed - reward=1"
    else
        echo "0" > "$REWARD_FILE"
        echo "Some tests failed - reward=0"
    fi
else
    echo "0" > "$REWARD_FILE"
    echo "No tests passed - reward=0"
fi

cat "$REWARD_FILE"
