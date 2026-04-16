#!/bin/bash
# Note: NOT using set -e because we want to capture pytest results even if some fail

# Install pytest if needed
pip install pytest pytest-asyncio -q

# Run tests and capture output
mkdir -p /logs/verifier
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt || true

# Write binary reward based on test results
# Count key test results - we need the core f2p tests to pass
passed=$(grep -c "PASSED" /logs/verifier/pytest_output.txt 2>/dev/null || echo "0")
failed=$(grep -o "FAILED" /logs/verifier/pytest_output.txt 2>/dev/null | wc -l || echo "0")

# Clean up any whitespace
passed=$(echo $passed | tr -d '[:space:]')
failed=$(echo $failed | tr -d '[:space:]')

# Binary reward: 1 if all tests pass (no failures), 0 otherwise
# This ensures complete implementation is required
if [ "$failed" = "0" ] && [ "$passed" -gt 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed ($passed total)"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: $failed tests failed, $passed passed"
fi

echo "Results: $passed passed, $failed failed"
cat /logs/verifier/reward.txt
