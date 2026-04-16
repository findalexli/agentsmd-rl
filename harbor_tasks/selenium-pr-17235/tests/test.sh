#!/bin/bash
# Standardized test runner for benchmark tasks
# Runs test_outputs.py and writes binary reward (0 or 1)

set -o pipefail

# Install pytest if not present
pip3 install pytest -q 2>/dev/null || true

# Ensure logs directory exists
mkdir -p /logs/verifier

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
