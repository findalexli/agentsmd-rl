#!/bin/bash

# Install pytest if needed
pip3 install pytest -q 2>/dev/null || pip install pytest -q 2>/dev/null || true

# Run tests and capture output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log
TEST_EXIT=${PIPESTATUS[0]}

# Write binary reward (1 if all tests pass, 0 otherwise)
# Check for "X passed" without "failed" in the summary line
OUTPUT=$(python3 -m pytest test_outputs.py -q 2>&1)
if echo "$OUTPUT" | grep -E "[0-9]+ passed" | grep -qv "failed"; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_EXIT
