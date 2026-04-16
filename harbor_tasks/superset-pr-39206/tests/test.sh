#!/bin/bash
# test.sh - Run tests and write binary reward
set -uo pipefail

# Ensure pytest is available
pip install --quiet pytest pytest-asyncio 2>/dev/null || true

# Run the tests
cd /workspace/superset
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log
test_result=${PIPESTATUS[0]}

# Write reward based on test result
if [ $test_result -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
