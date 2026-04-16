#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Install pytest if needed
pip3 install pytest -q 2>/dev/null || true

# Run pytest and capture results
cd /tests
set +e  # Disable exit on error to capture pytest exit code
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log
TEST_EXIT=${PIPESTATUS[0]}
set -e  # Re-enable exit on error

if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "Tests PASSED - Reward: 1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Tests FAILED - Reward: 0"
fi
