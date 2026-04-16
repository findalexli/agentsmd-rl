#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest -q 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run the tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write reward based on test results
if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
