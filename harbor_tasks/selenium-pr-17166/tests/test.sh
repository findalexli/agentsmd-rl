#!/bin/bash
# Standard test runner for benchmark tasks
set -e

# Install pytest if not present
pip3 install -q pytest 2>/dev/null || pip install -q pytest 2>/dev/null

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
