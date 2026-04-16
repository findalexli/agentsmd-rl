#!/bin/bash
set -e

# Install pytest if not already installed
pip install pytest pytest-asyncio pytest-mock freezegun -q 2>/dev/null || true

# Run the test_outputs.py file
cd /workspace/openhands

# Set up Python path
export PYTHONPATH="/workspace/openhands:/workspace/openhands/enterprise:$PYTHONPATH"

# Run tests with verbose output
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /tmp/pytest_output.txt

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
