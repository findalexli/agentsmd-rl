#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest --quiet --break-system-packages || pip3 install pytest --quiet

# Run tests and capture output
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
