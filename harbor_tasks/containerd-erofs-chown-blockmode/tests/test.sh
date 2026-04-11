#!/bin/bash
set -euo pipefail

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run tests and capture output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Count results - use head -1 to ensure single line output
PASSED=$(grep -c "test_outputs.py::.*PASSED" /logs/verifier/test_output.log 2>/dev/null | head -1 || echo "0")
FAILED=$(grep -c "test_outputs.py::.*FAILED" /logs/verifier/test_output.log 2>/dev/null | head -1 || echo "0")

# Trim whitespace
PASSED=$(echo "$PASSED" | tr -d '[:space:]')
FAILED=$(echo "$FAILED" | tr -d '[:space:]')

# Ensure we have numeric values
if ! [[ "$PASSED" =~ ^[0-9]+$ ]]; then PASSED=0; fi
if ! [[ "$FAILED" =~ ^[0-9]+$ ]]; then FAILED=0; fi

if [ "$FAILED" -eq 0 ] && [ "$PASSED" -ge 6 ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "All tests passed!" >> /logs/verifier/test_output.log
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "Some tests failed: $FAILED failures, $PASSED passed" >> /logs/verifier/test_output.log
fi

cat /logs/verifier/reward.txt
