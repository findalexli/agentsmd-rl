#!/bin/bash

# Run pytest on test_outputs.py and write binary reward
cd /workspace
pip3 install pytest==8.3.4 -q 2>/dev/null
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 || true

# Write reward: 1 if all tests passed, 0 otherwise
if python3 -m pytest /tests/test_outputs.py -v --tb=short --quiet 2>&1; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
