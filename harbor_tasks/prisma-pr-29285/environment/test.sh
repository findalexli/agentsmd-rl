#!/bin/bash

pip install pytest -q
cd /tests
pytest test_outputs.py -v --tb=short
PYTEST_RESULT=$?

# Write binary reward
if [ $PYTEST_RESULT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
