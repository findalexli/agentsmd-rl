#!/bin/bash

# Run pytest on test_outputs.py
cd /tests
python3 -m pytest test_outputs.py -v --tb=short

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ $? -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi