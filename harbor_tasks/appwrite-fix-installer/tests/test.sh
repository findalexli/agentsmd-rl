#!/bin/bash

# Install pytest if needed
pip install pytest 2>&1 | tail -3 || true

# Run tests
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1

# Write reward
if [ $? -eq 0 ]; then
    echo -en '\x01\x00\x01' > /logs/verifier/reward.txt
else
    echo -en '\x01\x00\x00' > /logs/verifier/reward.txt
fi