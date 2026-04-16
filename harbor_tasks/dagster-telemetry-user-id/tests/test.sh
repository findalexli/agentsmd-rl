#!/bin/bash

# Ensure log directory exists
mkdir -p /logs/verifier

# Install pytest if not available
pip install pytest pyyaml ruff -q

# Run tests and capture results
cd /workspace/dagster

# Run pytest with verbose output and capture to log (allow failure)
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log || true

# Check test results and write binary reward
# Count passed tests (strip whitespace)
PASSED=$(grep -c "PASSED" /logs/verifier/pytest_output.log 2>/dev/null | tr -d '[:space:]' || echo "0")
FAILED=$(grep -c "FAILED" /logs/verifier/pytest_output.log 2>/dev/null | tr -d '[:space:]' || echo "0")
ERROR=$(grep -c "ERROR" /logs/verifier/pytest_output.log 2>/dev/null | tr -d '[:space:]' || echo "0")

# Default to 0 if empty
PASSED=${PASSED:-0}
FAILED=${FAILED:-0}
ERROR=${ERROR:-0}

# Calculate reward: all tests must pass for reward=1
TOTAL_FAIL=$((FAILED + ERROR))

if [ "$TOTAL_FAIL" -eq 0 ] && [ "$PASSED" -gt 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed ($PASSED passed)"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: $FAILED failed, $ERROR errors, $PASSED passed"
fi

cat /logs/verifier/reward.txt
