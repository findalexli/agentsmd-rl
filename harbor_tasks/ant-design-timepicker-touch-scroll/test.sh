#!/bin/bash
set -e

# Install pytest (using --break-system-packages since this is a container)
pip install pytest -q --break-system-packages

# Run the tests and capture output
cd /workspace
python3 -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Extract test results for reward calculation
# Count passed tests
PASSED=$(grep -c "PASSED" /logs/verifier/test_output.log 2>/dev/null || echo "0")
FAILED=$(grep -c "FAILED" /logs/verifier/test_output.log 2>/dev/null || echo "0")
ERRORS=$(grep -c "ERROR" /logs/verifier/test_output.log 2>/dev/null || echo "0")
# Strip any whitespace/newlines
PASSED=$(echo "$PASSED" | tr -d '[:space:]')
FAILED=$(echo "$FAILED" | tr -d '[:space:]')
ERRORS=$(echo "$ERRORS" | tr -d '[:space:]')
TOTAL=$((PASSED + FAILED + ERRORS))

# Calculate binary reward (all tests must pass)
if [ "$FAILED" -eq 0 ] && [ "$ERRORS" -eq 0 ] && [ "$PASSED" -gt 0 ]; then
    REWARD=1
else
    REWARD=0
fi

# Write reward to file
echo "$REWARD" > /logs/verifier/reward.txt

echo ""
echo "================================"
echo "Tests: $PASSED passed, $FAILED failed, $ERRORS errors"
echo "Reward: $REWARD"
echo "================================"

# Return appropriate exit code
if [ "$REWARD" -eq 1 ]; then
    exit 0
else
    exit 1
fi
