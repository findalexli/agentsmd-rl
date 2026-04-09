#!/bin/bash
set -e

# Standardized test runner
REWARD_LOG="/logs/verifier/reward.txt"

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run tests
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward (1 if all tests pass, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > "$REWARD_LOG"
else
    echo "0" > "$REWARD_LOG"
fi
