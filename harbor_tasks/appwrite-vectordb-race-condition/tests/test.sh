#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --quiet 2>/dev/null || true

# Run the test suite
python3 /workspace/task/tests/test_outputs.py

# Write binary reward (1 if tests passed, 0 otherwise)
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
