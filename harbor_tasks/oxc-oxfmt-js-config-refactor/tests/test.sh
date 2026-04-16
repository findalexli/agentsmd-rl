#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest || true

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
REWARD=0
if python3 /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt; then
    # Count passed tests (use tr to remove any newlines)
    PASSED=$(grep -c "PASSED" /logs/verifier/pytest_output.txt 2>/dev/null | tr -d '\n' || echo "0")
    FAILED=$(grep -c "FAILED" /logs/verifier/pytest_output.txt 2>/dev/null | tr -d '\n' || echo "0")

    # Reward is 1 if all tests pass, 0 otherwise
    if [ "$FAILED" -eq 0 ] && [ "$PASSED" -gt 0 ]; then
        REWARD=1
    fi
fi

# Write binary reward
echo "$REWARD" > /logs/verifier/reward.txt
echo "Reward: $REWARD"

exit 0
