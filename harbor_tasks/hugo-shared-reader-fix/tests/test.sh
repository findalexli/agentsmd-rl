#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest pytest-timeout --break-system-packages 2>/dev/null || pip3 install pytest pytest-timeout --break-system-packages || true

# Run the test file with timeout handling
cd /workspace/hugo

# Create the reward file path
REWARD_FILE=/logs/verifier/reward.txt
mkdir -p /logs/verifier

# Run pytest with verbose output and capture results
if python3 -m pytest /tests/test_outputs.py -v --tb=short --timeout=300 2>&1; then
    echo "1" > "$REWARD_FILE"
    echo "SUCCESS: All tests passed"
else
    echo "0" > "$REWARD_FILE"
    echo "FAILURE: Some tests failed"
    exit 1
fi
