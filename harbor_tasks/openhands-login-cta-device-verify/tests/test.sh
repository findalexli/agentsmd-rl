#!/bin/bash
set -e

# Install pytest (using --break-system-packages for Docker env)
pip install pytest --quiet --break-system-packages

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
