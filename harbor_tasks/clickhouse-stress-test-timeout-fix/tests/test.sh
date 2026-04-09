#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest -q

# Run tests and write binary reward
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
