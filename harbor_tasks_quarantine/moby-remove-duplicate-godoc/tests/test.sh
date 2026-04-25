#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest pyyaml -q --break-system-packages 2>/dev/null || true

# Run tests and capture results
cd /tests
pytest test_outputs.py -v --tb=short > /logs/verifier/pytest_output.txt 2>&1 || true

# Check test results from output
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -qE "(FAILED|ERROR)" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    exit 0
else
    echo "0" > /logs/verifier/reward.txt
    exit 1
fi
