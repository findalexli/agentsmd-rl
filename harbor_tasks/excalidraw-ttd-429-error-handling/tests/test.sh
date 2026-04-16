#!/bin/bash

# Install pytest if needed (ignore warnings)
pip3 install pytest --quiet --break-system-packages 2>/dev/null || true

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short > /logs/verifier/pytest_output.txt 2>&1
TEST_EXIT=$?

# Write binary reward
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

# Always return success so the test runner can collect results
exit 0
