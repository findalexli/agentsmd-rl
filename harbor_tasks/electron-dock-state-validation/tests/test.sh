#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest pyyaml --break-system-packages 2>/dev/null || pip3 install pytest pyyaml

# Run tests
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Extract pass/fail counts
PASSED=$(grep -oP '\d+ passed' /logs/verifier/pytest_output.log | grep -oP '\d+' || echo "0")
FAILED=$(grep -oP '\d+ failed' /logs/verifier/pytest_output.log | grep -oP '\d+' || echo "0")
ERRORS=$(grep -oP '\d+ error' /logs/verifier/pytest_output.log | grep -oP '\d+' || echo "0")

TOTAL=$((PASSED + FAILED + ERRORS))

if [ "$TOTAL" -eq 0 ]; then
    TOTAL=$(grep -oP 'collected \d+ items' /logs/verifier/pytest_output.log | grep -oP '\d+' || echo "0")
fi

# Write binary reward file
if [ "$FAILED" -eq 0 ] && [ "$ERRORS" -eq 0 ] && [ "$TOTAL" -gt 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

echo "Tests completed: $PASSED passed, $FAILED failed, $ERRORS errors"
exit 0
