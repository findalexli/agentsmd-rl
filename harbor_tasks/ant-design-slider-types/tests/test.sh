#!/bin/bash

# Run tests and capture result (don't use set -e here)
python3 -m pytest /tests/test_outputs.py -v --tb=short || true

# Get the actual result
python3 -m pytest /tests/test_outputs.py --tb=no -q 2>/dev/null
TEST_RESULT=$?

# Write binary reward (1 if tests passed, 0 if failed)
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

echo "Test completed with exit code: $TEST_RESULT"
exit $TEST_RESULT
