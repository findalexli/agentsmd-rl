#!/bin/bash

# Ensure logs directory exists
mkdir -p /logs/verifier

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip install pytest
fi

# Run the tests and capture results
cd /tests
set +e
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_RESULT=${PIPESTATUS[0]}
set -e

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
