#!/bin/bash
set -e

# Install pytest
pip install pytest -q

# Run tests
cd /tests || cd /workspace/task/tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write reward (1 if all tests passed, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
