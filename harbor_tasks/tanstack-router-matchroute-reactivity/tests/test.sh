#!/bin/bash

# Install pytest
pip3 install pytest --quiet --break-system-packages

# Run the test suite and capture result
if python3 /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
    exit 0
else
    echo "0" > /logs/verifier/reward.txt
    exit 1
fi
