#!/bin/bash

# Install pytest if not present
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run tests and capture exit code
cd /tests
python3 -m pytest test_outputs.py -v --tb=short
TEST_RESULT=$?

# Write reward based on test result
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
