#!/bin/bash
# Standard test runner - DO NOT MODIFY
# Runs test_outputs.py and writes binary reward

set -e

# Install pytest if not available
pip3 install pytest -q 2>/dev/null || true

# Run pytest and capture exit code
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_EXIT_CODE=${PIPESTATUS[0]}

# Write binary reward based on test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
