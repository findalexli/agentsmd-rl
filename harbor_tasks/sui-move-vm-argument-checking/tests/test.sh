#!/bin/bash

# Install pytest if needed
python3 -m pytest --version > /dev/null 2>&1 || pip3 install pytest --break-system-packages

# Run tests and capture exit code (don't exit on failure)
python3 -m pytest /tests/test_outputs.py -v --tb=short
EXIT_CODE=$?

# Write binary reward
mkdir -p /logs/verifier
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed"
fi

exit $EXIT_CODE
