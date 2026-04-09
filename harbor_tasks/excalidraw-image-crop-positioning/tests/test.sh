#!/bin/bash
set -e

cd /workspace

# Install pytest if needed
pip3 install pytest pyyaml --break-system-packages 2>/dev/null || pip3 install pytest pyyaml --user 2>/dev/null || true

# Run the tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Extract test results
TEST_EXIT_CODE=${PIPESTATUS[0]}

# Count passed/failed tests
PASSED=$(grep -oP '\d+ passed' /logs/verifier/test_output.log | grep -oP '\d+' | awk '{s+=$1} END {print s}')
FAILED=$(grep -oP '\d+ failed' /logs/verifier/test_output.log | grep -oP '\d+' | awk '{s+=$1} END {print s}')
ERRORS=$(grep -oP '\d+ error' /logs/verifier/test_output.log | grep -oP '\d+' | awk '{s+=$1} END {print s}')

PASSED=${PASSED:-0}
FAILED=${FAILED:-0}
ERRORS=${ERRORS:-0}

TOTAL=$((PASSED + FAILED + ERRORS))

# Write binary reward
if [ "$TEST_EXIT_CODE" -eq 0 ] && [ "$FAILED" -eq 0 ] && [ "$ERRORS" -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

echo "Tests: $PASSED passed, $FAILED failed, $ERRORS errors (total: $TOTAL)"
echo "Reward: $(cat /logs/verifier/reward)"

exit $TEST_EXIT_CODE
