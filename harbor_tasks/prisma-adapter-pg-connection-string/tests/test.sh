#!/bin/bash

pip install pytest==8.3.4 requests==2.32.3 > /dev/null 2>&1

cd /tests
python -m pytest test_outputs.py -v --tb=short; ec=$?

# Write reward: 1 if all tests passed, 0 otherwise
if [ "$ec" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi