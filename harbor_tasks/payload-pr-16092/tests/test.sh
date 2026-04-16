#!/bin/bash

pip install pytest -q 2>/dev/null

python -m pytest /tests/test_outputs.py -v --tb=short --no-header

# Write binary reward
if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
