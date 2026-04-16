#!/bin/bash

pip3 install pytest --break-system-packages --quiet 2>/dev/null || true

cd /tests

python3 -m pytest test_outputs.py -v --tb=short
TEST_RESULT=$?

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ $TEST_RESULT -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi
