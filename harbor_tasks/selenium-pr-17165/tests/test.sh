#!/bin/bash
# Standard test runner for benchmark tasks
# Runs pytest on test_outputs.py and writes binary reward

set -e

# Install pytest if needed
pip install --quiet pytest

# Run tests and capture result
cd /tests
if pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
