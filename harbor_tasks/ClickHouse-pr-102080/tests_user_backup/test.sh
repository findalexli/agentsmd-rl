#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --quiet --break-system-packages 2>/dev/null || true

# Run tests and capture output
mkdir -p /logs/verifier

if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
