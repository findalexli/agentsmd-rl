#!/bin/bash

cd /workspace/mantine_repo

# Run pytest and capture exit code
python3 -m pytest /tests/test_outputs.py -v --tb=short --no-header
PYTEST_EXIT=$?

# Binary reward: pytest success (exit 0) = reward 1, pytest failure (exit 1) = reward 0
if [ $PYTEST_EXIT -eq 0 ]; then
    REWARD=1
else
    REWARD=0
fi

echo -n "$REWARD" > /logs/verifier/reward.txt

exit 0