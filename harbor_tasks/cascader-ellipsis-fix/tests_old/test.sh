#!/bin/bash
set -e

REPO_DIR="/workspace/ant-design"
LOGS_DIR="/logs/verifier"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Install pytest if not available
pip3 install pytest --quiet 2>/dev/null || pip install pytest --quiet 2>/dev/null

# Run the test file directly to get the REWARD output
python3 /tests/test_outputs.py 2>&1 | tee "$LOGS_DIR/test_output.log"

# Extract the binary reward from the test output
# The test should output a line like "REWARD: 1" or "REWARD: 0"
if grep -q "REWARD:" "$LOGS_DIR/test_output.log"; then
    REWARD=$(grep "REWARD:" "$LOGS_DIR/test_output.log" | tail -1 | sed 's/.*REWARD: \([0-9.]*\).*/\1/')
    echo ""
    echo "========================================"
    echo "FINAL REWARD: $REWARD"
    echo "========================================"
    # Write reward to a file for the harness
    echo "$REWARD" > "$LOGS_DIR/reward.txt"
else
    echo "No REWARD line found in test output"
    echo "0" > "$LOGS_DIR/reward.txt"
fi
