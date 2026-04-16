#!/bin/bash
set -e

cd /workspace/dagster

# Install pytest if not present
pip install --quiet pytest pytest-asyncio

# Run the test suite (allow failure due to set -e)
python -m pytest /tests/test_outputs.py -v --tb=short && PYTEST_RESULT=1 || PYTEST_RESULT=0

# Write reward (0=fail, 1=pass)
echo -n $PYTEST_RESULT > /logs/verifier/reward.txt