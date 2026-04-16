#!/bin/bash
set -e

# Install pytest
pip install pytest -q

# Run tests and capture output
cd /workspace/OpenHands
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

echo "Tests completed. Reward written to /logs/verifier/reward.txt"
