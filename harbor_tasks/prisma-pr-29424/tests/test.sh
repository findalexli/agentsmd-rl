#!/bin/bash

# Install pytest (using --break-system-packages for Debian-based images)
pip3 install pytest --break-system-packages -q

# Run tests
python3 -m pytest /tests/test_outputs.py -v --tb=short
TEST_RESULT=$?

# Write reward (0 or 1) based on test results
if [ $TEST_RESULT -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi

echo "Reward written: $(cat /logs/verifier/reward.txt)"