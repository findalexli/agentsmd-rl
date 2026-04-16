#!/bin/bash

cd /workspace/electric/packages/typescript-client

# Run pytest on the test_outputs.py
python3 -m pytest /tests/test_outputs.py -v --tb=short
result=$?

# Write reward
if [ $result -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi