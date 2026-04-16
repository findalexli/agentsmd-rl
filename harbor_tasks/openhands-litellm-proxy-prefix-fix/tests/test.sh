#!/bin/bash
# Standardized test harness for benchmark tasks
# DO NOT MODIFY - this is standardized boilerplate

set -eo pipefail

LOG_DIR="/logs/verifier"
REWARD_FILE="$LOG_DIR/reward.txt"
mkdir -p "$LOG_DIR"

# Install pytest if not present
pip install pytest pytest-asyncio httpx -q 2>/dev/null || true

# Run tests and capture output
cd /workspace/OpenHands
if pytest /tests/test_outputs.py -v --tb=short > "$LOG_DIR/pytest_output.txt" 2>&1; then
    echo "1" > "$REWARD_FILE"
else
    echo "0" > "$REWARD_FILE"
fi

echo "Test complete. Reward written to $REWARD_FILE"
cat "$REWARD_FILE"
