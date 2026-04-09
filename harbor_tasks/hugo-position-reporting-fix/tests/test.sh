#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run the test suite
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Extract pass/fail counts and write binary reward
PASSED=$(grep -oP '\d+ passed' /logs/verifier/test_output.log | grep -oP '\d+' | head -1 || echo "0")
FAILED=$(grep -oP '\d+ failed' /logs/verifier/test_output.log | grep -oP '\d+' | head -1 || echo "0")
TOTAL=$((PASSED + FAILED))

if [ "$FAILED" -eq "0" ] && [ "$PASSED" -gt "0" ]; then
    echo 1 > /logs/verifier/reward
    echo "All tests passed!"
else
    echo 0 > /logs/verifier/reward
    echo "Some tests failed: $FAILED failed, $PASSED passed"
fi
