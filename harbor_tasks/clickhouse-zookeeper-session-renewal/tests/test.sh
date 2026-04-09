#!/bin/bash
set -e

REPO="/workspace/ClickHouse"
TESTS_DIR="/tests"
LOGS_DIR="/logs/verifier"

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest --break-system-packages

# Run tests
cd "$REPO"
python3 -m pytest "$TESTS_DIR/test_outputs.py" -v --tb=short 2>&1 | tee "$LOGS_DIR/pytest_output.txt"

# Determine reward
if grep -q "passed" "$LOGS_DIR/pytest_output.txt" && ! grep -q "failed" "$LOGS_DIR/pytest_output.txt"; then
    echo "1" > "$LOGS_DIR/reward.txt"
else
    echo "0" > "$LOGS_DIR/reward.txt"
fi

echo "Reward: $(cat $LOGS_DIR/reward.txt)"
