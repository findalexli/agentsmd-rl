#!/bin/bash

# Install pytest if not already installed
pip install --quiet pytest

# Run tests and capture exit code
cd /tests
if python -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
