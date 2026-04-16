#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install pytest if not already installed
pip install --break-system-packages pytest 2>/dev/null || pip install pytest 2>/dev/null || true

# Run tests and capture output
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
    exit 1
fi
