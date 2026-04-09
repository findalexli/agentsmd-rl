#!/bin/bash
set -e

# Install pytest
pip install pytest pytest-asyncio -q

# Run tests and capture output
cd /workspace/openhands
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Determine reward based on test results
if grep -q "passed" /logs/verifier/test_output.log && ! grep -q "FAILED" /logs/verifier/test_output.log; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0"
fi
