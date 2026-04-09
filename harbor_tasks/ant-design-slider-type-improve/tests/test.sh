#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --quiet 2>/dev/null || pip install pytest --quiet 2>/dev/null || true

# Ensure log directory exists
mkdir -p /logs/verifier

# Run the test suite
if python3 /tests/test_outputs.py; then
    echo "1" > /logs/verifier/reward.txt
    exit 0
else
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi
