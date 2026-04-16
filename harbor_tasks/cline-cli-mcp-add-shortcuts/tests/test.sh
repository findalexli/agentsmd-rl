#!/bin/bash
# Note: not using set -e because we need to check test results manually

# Install pytest if not already installed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run tests with pytest
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt
PYTEST_EXIT=${PIPESTATUS[0]}

# Parse test counts from the summary line
# Extract numbers from "=== X passed, Y failed, Z warnings ==="
PASSED=$(grep -oE "[0-9]+ passed" /logs/verifier/pytest_output.txt 2>/dev/null | head -1 | grep -oE "[0-9]+" || echo "0")
FAILED=$(grep -oE "[0-9]+ failed" /logs/verifier/pytest_output.txt 2>/dev/null | head -1 | grep -oE "[0-9]+" || echo "0")

# If we didn't get values from summary, fall back to test definition count
if [ -z "$PASSED" ] || [ "$PASSED" = "" ]; then
    PASSED="0"
fi
if [ -z "$FAILED" ] || [ "$FAILED" = "" ]; then
    FAILED="0"
fi

# Count total tests from test file
TOTAL=$(grep -c "^def test_" /tests/test_outputs.py 2>/dev/null || echo "0")

# Strip any whitespace
TOTAL=$(echo "$TOTAL" | tr -d '[:space:]')
PASSED=$(echo "$PASSED" | tr -d '[:space:]')
FAILED=$(echo "$FAILED" | tr -d '[:space:]')

echo "Tests: $PASSED passed, $FAILED failed (out of $TOTAL total)"
echo "Pytest exit code: $PYTEST_EXIT"

# All tests must pass for reward=1
if [ "$FAILED" -eq 0 ] && [ "$PASSED" -gt 0 ] && [ "$PASSED" -eq "$TOTAL" ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi

cat /logs/verifier/reward.txt
