#!/bin/bash

# Run the test file
python3 -m pytest /tests/test_outputs.py -v --tb=short

# Write reward based on exit code
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
exit 0
