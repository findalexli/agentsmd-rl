#!/bin/bash
set -e

# Standardized test runner for benchmark tasks
# This installs pytest and runs test_outputs.py

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Create logs directory
mkdir -p /logs/verifier

# Run the tests - note: tests are mounted at /tests, not /workspace/task/tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $EXIT_CODE
