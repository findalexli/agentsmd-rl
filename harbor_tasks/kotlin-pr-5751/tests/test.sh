#!/bin/bash

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the Python test file and capture output
python3 -m pytest /tests/test_outputs.py -v 2>&1 | tee /tmp/test_output.txt

# Calculate reward based on test results
# Check for FAILED in the output
if grep -q "FAILED" /tmp/test_output.txt; then
    reward="0"
else
    reward="1"
fi

# Write reward to file
echo "$reward" > /logs/verifier/reward.txt

# Count tests
total_tests=$(grep -c "^../../tests/test_outputs.py::test_" /tmp/test_output.txt || echo "0")
passed_tests=$(grep -c "PASSED" /tmp/test_output.txt || echo "0")
failed_tests=$(grep -c "FAILED" /tmp/test_output.txt || echo "0")

echo ""
echo "=== TEST SUMMARY ==="
echo "Total tests: $total_tests"
echo "Passed: $passed_tests"
echo "Failed: $failed_tests"
echo "Reward: $reward"

# Return 0 if all tests passed, 1 otherwise
if [ "$reward" = "1" ]; then
    echo ""
    echo "=== TEST RESULT: PASSED ==="
    exit 0
else
    echo ""
    echo "=== TEST RESULT: FAILED ==="
    exit 1
fi
