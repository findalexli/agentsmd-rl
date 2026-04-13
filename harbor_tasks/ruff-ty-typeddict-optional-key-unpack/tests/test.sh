#!/bin/bash
# Test runner script

cd /workspace/calculator

# Run pytest on test_outputs.py
python3 -m pytest /tests/test_outputs.py -v

# Write reward based on exit code
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
