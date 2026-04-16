#!/bin/bash
set -e

# Use python3 explicitly
PYTHON=python3

# Install pytest if not present
pip3 install pytest -q --break-system-packages 2>/dev/null || pip3 install pytest -q

# Run tests and capture results
cd /workspace/superset

if $PYTHON -m pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
