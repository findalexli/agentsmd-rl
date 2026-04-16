#!/bin/bash

# Install pytest
python3 -m pip install pytest --quiet --break-system-packages 2>/dev/null || python3 -m pip install pytest --quiet 2>/dev/null || true

# Run the tests and capture exit code
cd /workspace
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_EXIT_CODE=${PIPESTATUS[0]}

# Determine reward based on test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
