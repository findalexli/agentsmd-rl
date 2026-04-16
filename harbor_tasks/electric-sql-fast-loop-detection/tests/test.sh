#!/usr/bin/env bash

# pytest is pre-installed via python3-pytest system package

# Run verification tests
python3 -m pytest /tests/test_outputs.py -v --tb=short

# Write reward
if [ $? -eq 0 ]; then
    echo -n "1" > /logs/verifier/reward.txt
else
    echo -n "0" > /logs/verifier/reward.txt
fi