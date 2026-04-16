#!/bin/bash

pip install pytest -q

pytest /tests/test_outputs.py -v --tb=short --no-header
TEST_RESULT=$?

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi
