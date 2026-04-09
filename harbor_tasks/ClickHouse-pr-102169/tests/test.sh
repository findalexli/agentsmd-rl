#!/bin/bash
# Standard test runner - DO NOT MODIFY
# Installs pytest, runs test_outputs.py, writes binary reward

set -e

# Ensure logs directory exists
mkdir -p /logs/verifier

# Install pytest if not present
pip install pytest --quiet 2>/dev/null || true

# Run tests and capture output
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0"
fi
