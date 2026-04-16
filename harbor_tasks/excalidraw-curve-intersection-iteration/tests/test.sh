#!/bin/bash

# Install pytest if needed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run the test suite
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1

# Capture exit code immediately
TEST_RESULT=$?

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_RESULT
