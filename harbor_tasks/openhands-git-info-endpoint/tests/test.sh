#!/bin/bash

# Install pytest if not already installed
pip install pytest pytest-asyncio -q 2>/dev/null || true

# Run tests and capture output
cd /workspace/openhands
python -m pytest /tests/test_outputs.py -v --tb=short > /logs/verifier/test_output.log 2>&1 || true

# Check for failures
if grep -q 'FAILED' /logs/verifier/test_output.log; then
    REWARD=0
else
    # Check if any tests passed
    if grep -q 'PASSED' /logs/verifier/test_output.log; then
        REWARD=1
    else
        REWARD=0
    fi
fi

cat /logs/verifier/test_output.log
echo ""
echo "Reward: $REWARD"

# Write binary reward
echo "$REWARD" > /logs/verifier/reward.txt
