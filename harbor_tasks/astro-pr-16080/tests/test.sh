#!/bin/bash

# Install pytest
pip3 install pytest --quiet --break-system-packages

# Run tests with verbose output
python3 -m pytest /tests/test_outputs.py -v --tb=short --no-header

# Write reward (0=fail, 1=pass)
if [ $? -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi
