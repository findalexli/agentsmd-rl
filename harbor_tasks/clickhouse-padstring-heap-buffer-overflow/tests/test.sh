#!/bin/bash

# Install pytest if needed
pip3 install --break-system-packages pytest 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run the Python test
if python3 -m pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
