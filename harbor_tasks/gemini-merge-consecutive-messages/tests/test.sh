#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run tests and capture output
pytest /workspace/task/tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (1 if all tests passed, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /workspace/task/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /workspace/task/reward.txt
    echo "FAILURE: Some tests failed"
fi
