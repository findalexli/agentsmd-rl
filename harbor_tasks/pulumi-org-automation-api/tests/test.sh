#!/bin/bash

# Install pytest if needed
pip install pytest -q 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run the test suite and capture exit code
if python3 /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
