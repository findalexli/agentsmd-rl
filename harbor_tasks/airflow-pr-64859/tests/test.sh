#!/bin/bash

# Install pytest if not available
pip install --quiet pytest 2>/dev/null || true

# Run the tests and capture exit code
cd /tests
python -m pytest test_outputs.py -v --tb=short
TEST_EXIT_CODE=$?

# Write reward based on test result
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_EXIT_CODE
