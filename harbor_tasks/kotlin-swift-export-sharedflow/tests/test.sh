#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest -q 2>/dev/null || true

# Run the tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /tmp/pytest_output.txt || true

# Determine reward: 1 if all tests pass, 0 otherwise
REWARD=0
if grep -q "passed" /tmp/pytest_output.txt && ! grep -q "FAILED" /tmp/pytest_output.txt; then
    REWARD=1
fi

# Write binary reward
mkdir -p /logs/verifier
echo "$REWARD" > /logs/verifier/reward.txt
echo "Reward: $REWARD"
