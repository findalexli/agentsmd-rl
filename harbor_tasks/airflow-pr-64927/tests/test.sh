#!/bin/bash
# Standard test runner for benchmark tasks

# Install pytest if not available
pip install --quiet pytest

# Run the tests and capture exit code
cd /tests
python -m pytest test_outputs.py -v --tb=short
TEST_EXIT_CODE=$?

# Determine reward based on test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
