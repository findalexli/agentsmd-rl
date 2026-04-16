#!/bin/bash
set -e

echo "=== Setting up test environment ==="

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest --user 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

echo "=== Running pytest ==="
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Check if all tests passed
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -qE "(failed|error|FAILED|ERROR)" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "=== SUCCESS: All tests passed ==="
else
    echo "0" > /logs/verifier/reward.txt
    echo "=== FAILURE: Some tests failed ==="
fi

cat /logs/verifier/reward.txt
