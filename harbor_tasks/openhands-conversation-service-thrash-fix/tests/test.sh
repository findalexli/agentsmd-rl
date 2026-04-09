#!/bin/bash

# Install pytest if not available
pip install pytest pytest-asyncio -q 2>/dev/null || true

# Run the tests and capture output (don't exit on failure)
cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Check if all tests passed by looking for "N passed" and no "failed"
passed_count=$(grep -oE "[0-9]+ passed" /logs/verifier/test_output.log | grep -oE "[0-9]+" | head -1)
failed_count=$(grep -oE "[0-9]+ failed" /logs/verifier/test_output.log | grep -oE "[0-9]+" | head -1)

if [ -n "$passed_count" ] && [ -z "$failed_count" ]; then
    # All tests passed (no failures)
    echo "1" > /logs/verifier/reward.txt
else
    # Some tests failed
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
