#!/bin/bash
set -e

# Ensure pytest is installed (may already be in image)
if ! python3 -m pytest --version > /dev/null 2>&1; then
    pip3 install pytest --break-system-packages --quiet
fi

# Run tests and capture results
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
