#!/bin/bash
# Standardized test runner for task verification
# Do NOT modify this file - it is standardized boilerplate

set -e

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest
fi

# Create log directory
mkdir -p /logs/verifier

# Run tests and capture output
pytest /workspace/tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
