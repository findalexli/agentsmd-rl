#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest pyyaml --break-system-packages 2>/dev/null || pip3 install pytest pyyaml

# Create log directory
mkdir -p /logs/verifier

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0"
fi
