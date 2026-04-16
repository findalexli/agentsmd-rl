#!/bin/bash
set -e

# Install pytest using pip with break-system-packages flag (needed for Debian-based images)
python3 -m pip install --quiet --break-system-packages pytest

# Run tests and capture result
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_RESULT=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
