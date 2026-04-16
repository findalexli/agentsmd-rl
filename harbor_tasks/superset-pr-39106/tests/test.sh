#!/bin/bash
# Standardized test runner for benchmark tasks
# DO NOT MODIFY - this is boilerplate

set -e

# Ensure pytest is available
pip install --quiet pytest 2>/dev/null || true

# Run tests and capture result
cd /workspace
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
