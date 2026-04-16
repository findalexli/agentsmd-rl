#!/bin/bash
set -e

# Use the pre-installed venv
export PATH="/opt/venv/bin:$PATH"

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
