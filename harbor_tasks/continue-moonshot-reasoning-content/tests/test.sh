#!/bin/bash

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test suite
cd /tests
python3 -m pytest test_outputs.py -v --tb=short
TEST_RESULT=$?

# Write binary reward to file
# If pytest succeeds (exit 0), reward=1, otherwise reward=0
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_RESULT
