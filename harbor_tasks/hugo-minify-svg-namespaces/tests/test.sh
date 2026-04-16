#!/bin/bash

# Install pytest if needed
pip install pytest --quiet 2>/dev/null || true

# Run the tests and capture result
python3 -m pytest /tests/test_outputs.py -v --tb=short
TEST_RESULT=$?

# Write reward file based on test results
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_RESULT
