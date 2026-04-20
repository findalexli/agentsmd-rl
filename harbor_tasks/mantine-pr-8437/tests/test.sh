#!/bin/bash

# Run pytest on test_outputs.py
pip install pytest==8.3.4 -q

cd /workspace
python -m pytest /tests/test_outputs.py -v --tb=short --no-header

# Write binary reward based on pytest exit code
if [ $? -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi
