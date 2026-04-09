#!/bin/bash
set -e

# Install pytest if not already installed (use --break-system-packages for system Python)
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet || true

# Run the tests and capture output
mkdir -p /logs/verifier
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward based on test results
REWARD=0
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    REWARD=1
fi

echo "$REWARD" > /logs/verifier/reward.txt
echo "Final reward: $REWARD"
