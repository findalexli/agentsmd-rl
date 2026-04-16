#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Installs pytest, runs test_outputs.py, writes binary reward

LOG_DIR="/logs/verifier"
REWARD_FILE="${LOG_DIR}/reward.txt"

mkdir -p "$LOG_DIR"

# Install pytest if not available
pip install pytest --quiet 2>/dev/null || true

# Run tests and capture results
cd /workspace/dagster || true

# Run pytest with verbose output and capture to file
python -m pytest /tests/test_outputs.py -v --tb=short > "${LOG_DIR}/pytest_output.txt" 2>&1 || true

# Simple parsing: count passed/failed
PASSED=$(grep -E "PASSED" "${LOG_DIR}/pytest_output.txt" 2>/dev/null | wc -l || echo "0")
FAILED=$(grep -E "FAILED" "${LOG_DIR}/pytest_output.txt" 2>/dev/null | wc -l || echo "0")
ERROR=$(grep -E "ERROR" "${LOG_DIR}/pytest_output.txt" 2>/dev/null | wc -l || echo "0")

# Trim whitespace
PASSED=$(echo "$PASSED" | tr -d ' ')
FAILED=$(echo "$FAILED" | tr -d ' ')
ERROR=$(echo "$ERROR" | tr -d ' ')

# Calculate reward: all tests must pass
TOTAL=$((PASSED + FAILED + ERROR))
if [ "$TOTAL" -eq 0 ]; then
    REWARD="0"
elif [ "$FAILED" -eq 0 ] && [ "$ERROR" -eq 0 ]; then
    REWARD="1"
else
    REWARD="0"
fi

# Write binary reward
echo "$REWARD" > "$REWARD_FILE"
exit 0
