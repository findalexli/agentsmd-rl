#!/bin/bash
set -e

# Install pytest if needed (using --break-system-packages for container environment)
pip install pytest --break-system-packages -q 2>/dev/null || pip install pytest -q 2>/dev/null || true

# Run tests and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt || true

# Check if all tests passed by looking for "passed" and no "failed"
output=$(cat /logs/verifier/pytest_output.txt)

# Write binary reward based on test results
# If we see "passed" and no "FAILED", reward=1
if echo "$output" | grep -q "passed" && ! echo "$output" | grep -q "FAILED"; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

# Exit with the original exit code
if echo "$output" | grep -q "FAILED"; then
    exit 1
else
    exit 0
fi
