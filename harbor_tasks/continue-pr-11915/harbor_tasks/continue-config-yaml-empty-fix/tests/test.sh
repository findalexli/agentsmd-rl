#!/bin/bash

cd /workspace

# Run pytest with verbose output and short traceback
set +e
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1
PYTEST_EXIT=$?
set -e

# Write binary reward
if [ $PYTEST_EXIT -eq 0 ]; then
    printf '\x01' > /logs/verifier/reward.txt
else
    printf '\x00' > /logs/verifier/reward.txt
fi