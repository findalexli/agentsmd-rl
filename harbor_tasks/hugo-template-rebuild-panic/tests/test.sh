#!/bin/bash

# Run pytest with the test file
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1

# Capture the exit status
exit_code=$?

# Write binary reward: 1 if all tests pass, 0 otherwise
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
