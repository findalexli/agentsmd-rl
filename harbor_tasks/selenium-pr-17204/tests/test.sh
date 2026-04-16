#!/bin/bash

# Install pytest if not present
pip install --quiet pytest 2>/dev/null || true

# Run the tests and capture exit code
cd /workspace/selenium
python -m pytest /tests/test_outputs.py -v --tb=short
TEST_EXIT_CODE=$?

# Write reward based on test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
