#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
cd /workspace
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
