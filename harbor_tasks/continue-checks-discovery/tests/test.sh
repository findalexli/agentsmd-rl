#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run the test file
cd /workspace/continue/extensions/cli
python3 -m pytest /tests/test_outputs.py -v 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests passed, 0 otherwise
# Check for the summary line with "X passed" and no "failed"
if grep -E "^[=]+ [0-9]+ passed( in)?" /logs/verifier/pytest_output.txt | grep -qv "failed"; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
