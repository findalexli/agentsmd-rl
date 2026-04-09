#!/bin/bash

# Create log directory if it doesn't exist
mkdir -p /logs/verifier

# Use the virtual environment's pytest
if /opt/venv/bin/pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
