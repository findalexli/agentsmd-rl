#!/bin/bash

cd /workspace

# Install pytest if needed
pip install --no-cache-dir pytest==8.3.4 -q

# Run tests
pytest /tests/test_outputs.py -v --tb=short --no-header -q

# Write reward
if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
