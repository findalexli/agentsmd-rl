#!/bin/bash
set -e

LOG_DIR="/logs/verifier"
REWARD_FILE="$LOG_DIR/reward.txt"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Install pytest if not available
pip install pytest -q 2>/dev/null || true

# Run tests
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee "$LOG_DIR/test_output.log"

# Write binary reward (1 if all passed, 0 if any failed)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > "$REWARD_FILE"
else
    echo "0" > "$REWARD_FILE"
fi
