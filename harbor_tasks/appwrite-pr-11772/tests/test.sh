#!/bin/bash
set -e

cd /workspace/task/tests

# Install pytest if not present
pip install pytest -q

# Run the tests and capture output
pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file
# Count passed tests
PASSED=$(grep -c "PASSED" /logs/verifier/test_output.log || echo "0")
TOTAL=$(grep -c "test_" /logs/verifier/test_outputs.py || echo "0")

# Calculate score as passed/total
if [ "$TOTAL" -gt 0 ]; then
    SCORE=$(python3 -c "print($PASSED / $TOTAL)")
else
    SCORE="0.0"
fi

# Write binary reward (0 or 1 based on all tests passing)
if grep -q "failed" /logs/verifier/test_output.log; then
    echo "0" > /logs/verifier/reward
    echo "Some tests failed"
    exit 1
else
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
    exit 0
fi
