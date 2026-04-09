#!/bin/bash
set -e

# Install pytest if not present
pip3 install -q pytest 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
