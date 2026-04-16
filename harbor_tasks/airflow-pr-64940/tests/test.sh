#!/bin/bash
# Standardized test runner for benchmark tasks
# Runs test_outputs.py and writes binary reward to /logs/verifier/reward.txt

set -e

# Ensure pytest is available
pip install --quiet pytest 2>/dev/null || true

# Run tests and capture result
cd /tests
if python -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
