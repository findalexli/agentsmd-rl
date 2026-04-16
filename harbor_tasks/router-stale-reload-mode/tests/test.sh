#!/bin/bash

# Create logs directory
mkdir -p /logs/verifier

# Run the tests
python3 /tests/test_outputs.py -v --tb=short

# Write binary reward
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
