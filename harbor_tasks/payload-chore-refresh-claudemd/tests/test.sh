#!/bin/bash
# Test script for the requests default_user_agent documentation task

set -e

# Install the requests package
cd /workspace/requests
pip install -e . --quiet 2>&1 | grep -v "WARNING: Running pip as the 'root' user" || true

# Run pytest on the test file
python -m pytest /tests/test_outputs.py -v 2>&1 | tee /tmp/test_output.txt

# Count results
PASSED=$(grep -c "PASSED" /tmp/test_output.txt || echo "0")
FAILED=$(grep -c "FAILED" /tmp/test_output.txt || echo "0")

echo ""
echo "Tests: $PASSED passed, $FAILED failed"
echo ""

# Determine overall result
mkdir -p /logs/verifier

# Count specific test types
# Note: Order matters - check fail_to_pass first (more specific pattern)
FAIL_TO_PASS_FAILED=$(grep -E "test_.*_fail_to_pass.*FAILED" /tmp/test_output.txt | wc -l || echo "0")
# For pass_to_pass, exclude lines that have fail_to_pass in them
PASS_TO_PASS_FAILED=$(grep -E "test_.*_pass_to_pass.*FAILED" /tmp/test_output.txt | grep -v "fail_to_pass" | wc -l || echo "0")
# Also exclude the summary line which shows "X failed"
TOTAL_FAILED=$(grep -E "^\s*=+\s*[0-9]+ failed" /tmp/test_output.txt | head -1 | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")

echo "Fail-to-pass tests failed: $FAIL_TO_PASS_FAILED"
echo "Pass-to-pass tests failed: $PASS_TO_PASS_FAILED"
echo "Total tests failed: $TOTAL_FAILED"

# Reward is 1 only if ALL tests pass (both fail_to_pass AND pass_to_pass)
if [ "$FAIL_TO_PASS_FAILED" -eq 0 ] && [ "$PASS_TO_PASS_FAILED" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    if [ "$PASS_TO_PASS_FAILED" -ne 0 ]; then
        echo "Some pass_to_pass tests failed!"
        exit 1
    fi
    echo "Some tests failed (expected for NOP test on buggy code)."
fi
