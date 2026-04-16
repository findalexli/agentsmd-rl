#!/bin/bash

# Install pytest if needed
pip install pytest -q 2>/dev/null || true

# Run the tests and capture the result
if pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
    exit 0
else
    echo "0" > /logs/verifier/reward.txt
    exit 1
fi
