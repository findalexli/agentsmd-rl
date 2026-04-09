#!/bin/bash
set -e

echo "=== Installing pytest ==="
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

echo "=== Running tests ==="
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

echo "=== Writing binary reward ==="
# Count passed tests
PASSED=$(python3 -m pytest test_outputs.py --tb=no -q 2>/dev/null | grep -oP '\d+ passed' | grep -oP '\d+' || echo "0")
TOTAL=$(python3 -m pytest test_outputs.py --collect-only -q 2>/dev/null | grep -oP '\d+ test' | grep -oP '\d+' || echo "0")

if [ -z "$PASSED" ]; then PASSED=0; fi
if [ -z "$TOTAL" ]; then TOTAL=0; fi

echo "Passed: $PASSED / $TOTAL"

# Write binary reward (1 if all tests pass, 0 otherwise)
if [ "$PASSED" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

echo "Reward written to /logs/verifier/reward.txt"
