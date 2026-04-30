#!/bin/bash
set -e

# Run tests and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Extract test results and write binary reward
# Count passed tests
PASSED=$(grep -c "PASSED" /logs/verifier/test_output.log || true)
FAILED=$(grep -c "FAILED" /logs/verifier/test_output.log || true)

TOTAL=$((PASSED + FAILED))

if [ "$TOTAL" -eq 0 ]; then
    echo "0" > /logs/verifier/reward.txt
elif [ "$FAILED" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

echo "Tests passed: $PASSED, failed: $FAILED, total: $TOTAL"
cat /logs/verifier/reward.txt
