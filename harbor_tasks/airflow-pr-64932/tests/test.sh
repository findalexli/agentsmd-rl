#!/bin/bash
# Standard test runner for benchmark tasks
# Runs pytest on test_outputs.py and writes binary reward

set -e

# Install pytest if needed
pip install --quiet pytest pyyaml jmespath 2>/dev/null || true

# Run tests
cd /tests
if pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
