#!/bin/bash
set -e

# Standardized test runner for Harbor benchmark tasks
# Runs pytest and outputs binary reward to /logs/verifier/reward.txt

LOGS_DIR="/logs/verifier"
REWARD_FILE="$LOGS_DIR/reward.txt"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Install pytest if not present
pip3 install pytest -q 2>/dev/null || true

# Run tests and capture output
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$REWARD_FILE"
    echo "All tests passed - reward=1"
else
    echo "0" > "$REWARD_FILE"
    echo "Some tests failed - reward=0"
fi

# Display reward
cat "$REWARD_FILE"
