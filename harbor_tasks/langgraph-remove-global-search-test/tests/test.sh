#!/bin/bash
set -e

# Install pytest if not already installed
pip install pytest pytest-asyncio -q

# Create log directory
mkdir -p /logs/verifier

# Run the test file
cd /workspace/langgraph
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward based on test results
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0"
fi
