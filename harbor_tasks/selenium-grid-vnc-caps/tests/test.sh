#!/bin/bash
set -e

# pytest is already installed in the Docker image

# Run the test suite
echo "Running test_outputs.py..."
python3 -m pytest /tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Check if tests passed
EXIT_CODE=${PIPESTATUS[0]}

# Write binary reward file (1 if all passed, 0 otherwise)
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $EXIT_CODE
