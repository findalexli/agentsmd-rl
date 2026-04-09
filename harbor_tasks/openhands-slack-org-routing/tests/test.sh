#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest pytest-asyncio -q

# Run the test suite
cd /workspace/openhands
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (0 or 1 based on test success)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
    exit 1
fi
