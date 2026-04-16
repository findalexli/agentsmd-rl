#!/bin/bash
# Test runner for benchmark task
# Standardized script - do not modify task-specific logic

set -e

# Install pytest if not available
pip install --quiet pytest pytest-asyncio 2>/dev/null || true

# Run tests and capture result
cd /workspace/superset
PYTHONPATH=/workspace/superset python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_RESULT=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
