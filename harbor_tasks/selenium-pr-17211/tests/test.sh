#!/bin/bash
# Standard test runner for benchmark tasks
# Installs pytest, runs test_outputs.py, and writes binary reward

set -e

# Ensure logs directory exists
mkdir -p /logs/verifier

# Install pytest if not present
pip3 install --quiet pytest 2>/dev/null || pip install --quiet pytest 2>/dev/null

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
