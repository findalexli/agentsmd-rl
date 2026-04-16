#!/bin/bash

cd /tests

# Run pytest; reward=1 if all pass, reward=0 if any fail
python3 -m pytest test_outputs.py -v --tb=short 2>&1
PYTEST_EXIT=$?

# Binary reward: 1 = all tests passed, 0 = any test failed
if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
