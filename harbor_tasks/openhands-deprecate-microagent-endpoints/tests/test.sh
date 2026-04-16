#!/bin/bash
set -e

cd /workspace/openhands

# Install pytest and other dependencies needed for testing
pip install pytest httpx sqlalchemy -q 2>/dev/null || pip install pytest httpx sqlalchemy -q

# Run tests and capture exit code
set +e
pytest /tests/test_outputs.py -v --tb=short 2>&1
TEST_EXIT=$?
set -e

# Check if all tests passed by looking at exit code and output
PASSED_COUNT=$(pytest /tests/test_outputs.py --tb=no -q 2>&1 | grep -oP '\d+ passed' | grep -oP '\d+' || echo "0")
FAILED_COUNT=$(pytest /tests/test_outputs.py --tb=no -q 2>&1 | grep -oP '\d+ failed' | grep -oP '\d+' || echo "0")

# Get total number of tests (count actual test functions in test file)
TOTAL_TESTS=$(grep -c "^def test_" /tests/test_outputs.py 2>/dev/null || echo "6")

# Write reward: 1 if all passed, 0 otherwise
if [ "$PASSED_COUNT" -eq "$TOTAL_TESTS" ] && [ "$FAILED_COUNT" -eq "0" ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0 (passed: $PASSED_COUNT, failed: $FAILED_COUNT)"
fi