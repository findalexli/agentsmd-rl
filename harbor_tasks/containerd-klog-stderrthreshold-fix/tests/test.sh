#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest -q 2>/dev/null || true

# Run the tests and capture output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Write binary reward
REWARD=0
if python3 -m pytest test_outputs.py -q 2>&1 | grep -q "passed"; then
    # Check if all tests passed (no failures)
    if ! python3 -m pytest test_outputs.py -q 2>&1 | grep -q "failed"; then
        REWARD=1
    fi
fi

echo "$REWARD" > /logs/verifier/reward.txt
echo "Reward: $REWARD"
