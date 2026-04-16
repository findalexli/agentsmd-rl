#!/bin/bash
set -e

cd /workspace/continue/packages/openai-adapters

# Install pytest if needed
pip3 install --break-system-packages pytest pytest-timeout -q

# Run the tests and capture result
set +e
pytest /tests/test_outputs.py -v --tb=short --timeout=120
PYTEST_RC=$?
set -e

# Write reward
if [ $PYTEST_RC -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi