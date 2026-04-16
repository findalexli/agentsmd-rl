#!/bin/bash
set -e

# Test script - runs pytest on test_outputs.py
# This script is standardized and should not be modified with task-specific logic.

cd /workspace

pip install pytest -q

pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/output.txt

# Write reward
if [ -f /logs/verifier/reward.txt ]; then
    cat /logs/verifier/reward.txt
else
    # Determine reward based on test results
    if grep -q "passed" /logs/verifier/output.txt && ! grep -q "failed" /logs/verifier/output.txt; then
        echo "1" > /logs/verifier/reward.txt
    else
        echo "0" > /logs/verifier/reward.txt
    fi
    cat /logs/verifier/reward.txt
fi