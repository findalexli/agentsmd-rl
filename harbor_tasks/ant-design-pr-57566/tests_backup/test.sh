#!/bin/bash
# Standardized test runner - DO NOT MODIFY
set -e

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet
fi

# Run tests and capture result
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log
TEST_RESULT=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_RESULT
