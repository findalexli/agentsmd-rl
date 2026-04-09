#!/bin/bash
set -e

# Install pytest if not already available
pip install -q pytest

# Run the tests
cd /workspace
pytest tests/test_outputs.py -v

# Write binary reward (1 if tests passed, 0 otherwise)
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
