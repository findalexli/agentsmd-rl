#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || true

# Run the tests
cd /workspace/openhands/frontend
python3 /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward (0 or 1) based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
