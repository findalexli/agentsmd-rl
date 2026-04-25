#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest --quiet --break-system-packages

# Run tests and capture results
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
