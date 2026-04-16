#!/bin/bash
set -e

# Install pytest with --break-system-packages since we're in a container
pip3 install pytest --quiet --break-system-packages

# Run tests and capture exit code
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt
TEST_EXIT_CODE=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
