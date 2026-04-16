#!/bin/bash
set -e

# Standardized test runner - DO NOT MODIFY
# Installs pytest, runs test_outputs.py, writes binary reward

# Install pytest if needed
pip3 install pytest pyyaml --break-system-packages 2>/dev/null || pip3 install pytest pyyaml

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture results
if pytest /tests/test_outputs.py -v --tb=short > /logs/verifier/pytest_output.txt 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "TESTS PASSED"
else
    echo "0" > /logs/verifier/reward.txt
    echo "TESTS FAILED"
fi

cat /logs/verifier/pytest_output.txt
