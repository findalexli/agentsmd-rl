#!/bin/bash

pip install pytest==8.3.4 -q

cd /tests

python -m pytest test_outputs.py -v --tb=short
TEST_RESULT=$?

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_RESULT