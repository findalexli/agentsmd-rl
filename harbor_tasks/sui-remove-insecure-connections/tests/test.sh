#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run the test file and capture output
cd /workspace/sui
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
