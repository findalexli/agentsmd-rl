#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Installs pytest and runs test_outputs.py

cd /workspace/kotlin

# Install pytest (use --break-system-packages for Docker environment)
pip3 install pytest -q --break-system-packages || pip3 install pytest -q

# Run tests with verbose output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
