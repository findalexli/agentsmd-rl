#!/bin/bash
# Test runner script
# Note: Don't use set -e because we want to capture test results

TESTS_DIR="/tests"
LOGS_DIR="/logs/verifier"

# Create logs directory
mkdir -p "$LOGS_DIR"

# Run the Python tests
cd "$TESTS_DIR"
python3 test_outputs.py > "$LOGS_DIR/test_output.txt" 2>&1
TEST_EXIT=$?

# Write reward based on result
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > "$LOGS_DIR/reward.txt"
    echo "All tests passed"
else
    echo "0" > "$LOGS_DIR/reward.txt"
    echo "Some tests failed"
fi

exit 0
