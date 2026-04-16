#!/bin/bash

# Run the test suite and capture exit code
python3 /tests/test_outputs.py -v --tb=short 2>&1
EXIT_CODE=$?

# Write reward: 1 if all tests pass, 0 otherwise
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0"
fi

exit 0
