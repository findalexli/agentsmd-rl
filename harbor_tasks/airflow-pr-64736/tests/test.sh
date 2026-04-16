#!/bin/bash
# Standardized test runner for benchmark tasks
# Installs pytest, runs test_outputs.py, writes binary reward

set -e

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet
fi

# Run tests and capture result
cd /tests
if pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
