#!/bin/bash
# Standard test runner for benchmark tasks
# Runs test_outputs.py and writes binary reward

set -e

# Ensure logs directory exists
mkdir -p /logs/verifier

# Install pytest if not available
pip3 install pytest --quiet --break-system-packages 2>/dev/null || python3 -m pip install pytest --quiet --break-system-packages 2>/dev/null || true

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
