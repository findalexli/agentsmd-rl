#!/usr/bin/env bash
set -e

# Standard test runner for agent benchmark tasks
# Runs pytest and writes reward to /logs/verifier/reward.txt

REWARD_FILE=/logs/verifier/reward.txt
mkdir -p "$(dirname "$REWARD_FILE")"

# Run pytest with verbose output
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$REWARD_FILE"
    echo "PASS: All tests passed"
else
    echo "0" > "$REWARD_FILE"
    echo "FAIL: Some tests failed"
fi

cat "$REWARD_FILE"
