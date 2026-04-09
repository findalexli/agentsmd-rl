#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Run pytest on test_outputs.py
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
