#!/bin/bash
set -o pipefail

# Install pytest if needed
python3 -m pip install --quiet --break-system-packages pytest 2>/dev/null || true

# Run tests and capture results
mkdir -p /logs/verifier
cd /tests

# Run pytest and capture exit code separately (don't use set -e for this)
python3 -m pytest test_outputs.py -v --tb=short > /logs/verifier/pytest_output.log 2>&1 || true

# Check for failure markers in the output
if grep -q "ERROR\|FAILED" /logs/verifier/pytest_output.log && ! grep -q "PASSED" /logs/verifier/pytest_output.log; then
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: All tests failed"
elif grep -q "FAILED" /logs/verifier/pytest_output.log; then
    # Some passed, some failed
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
else
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
fi

cat /logs/verifier/pytest_output.log
exit 0
