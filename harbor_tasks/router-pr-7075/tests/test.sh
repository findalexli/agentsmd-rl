#!/bin/bash
set -e

# Install pytest if not present
if ! command -v pytest &> /dev/null; then
    python3 -m pip install --quiet --break-system-packages pytest
fi

# Run tests and capture result
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log
TEST_RESULT=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
