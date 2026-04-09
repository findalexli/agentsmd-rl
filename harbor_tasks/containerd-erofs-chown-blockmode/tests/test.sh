#!/bin/bash
set -euo pipefail

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run tests and capture output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Count results
PASSED=$(grep -c "PASSED\|passed" /logs/verifier/test_output.log 2>/dev/null || echo "0")
FAILED=$(grep -c "FAILED\|failed\|ERROR\|error" /logs/verifier/test_output.log 2>/dev/null || echo "0")

# Write binary reward file (pass if all tests pass, fail if any fail)
# We have 6 tests, all must pass for reward=1.0
TOTAL_TESTS=6
PASSED_NUM=$(python3 -m pytest test_outputs.py --collect-only 2>/dev/null | grep "test session" | grep -oP '\d+' | head -1 || echo "$TOTAL_TESTS")

if [ "$FAILED" -eq "0" ] && [ "$PASSED" -ge "$TOTAL_TESTS" ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "All tests passed!" >> /logs/verifier/test_output.log
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "Some tests failed: $FAILED failures, $PASSED passed" >> /logs/verifier/test_output.log
fi

cat /logs/verifier/reward.txt
