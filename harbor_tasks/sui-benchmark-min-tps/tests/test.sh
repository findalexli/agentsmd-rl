#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || true

# Run the test file
cd /workspace/sui

# Run pytest and capture exit code without exiting on failure
set +e
pytest /tests/test_outputs.py -v --tb=short
PYTEST_EXIT=$?
set -e

# Write reward (1 if tests passed, 0 otherwise)
if [ $PYTEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
