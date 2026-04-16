#!/bin/bash
set -e

# pytest is pre-installed in the Docker image

# Run the tests
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_EXIT_CODE=${PIPESTATUS[0]}

# Write binary reward based on test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
