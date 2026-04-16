#!/bin/bash
set -e

# Install pytest (use --break-system-packages for Debian system Python)
pip install pytest --quiet --break-system-packages 2>/dev/null || \
    (apt-get update -qq && apt-get install -y -qq python3-pytest) || \
    pip install pytest --quiet 2>/dev/null

# Run tests and capture output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /tmp/pytest_output.txt || true

# Check if all tests passed
if grep -q "passed" /tmp/pytest_output.txt && ! grep -q "FAILED" /tmp/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

cat /tmp/pytest_output.txt
