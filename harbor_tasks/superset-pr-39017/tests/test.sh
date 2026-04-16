#!/bin/bash
# Standardized test runner for benchmark tasks
# DO NOT MODIFY - this is boilerplate

set -e

# Ensure pytest is available
pip install -q pytest pytest-asyncio 2>/dev/null || true

# Run tests and capture result
cd /workspace/superset
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_EXIT_CODE=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_EXIT_CODE
