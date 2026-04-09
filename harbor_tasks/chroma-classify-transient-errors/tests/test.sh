#!/bin/bash
set -e

cd /workspace/task/tests

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (0 = fail, 1 = pass)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed"
    exit 1
fi
