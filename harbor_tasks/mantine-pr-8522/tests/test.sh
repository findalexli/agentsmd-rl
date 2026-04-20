#!/bin/bash

cd /workspace/mantine

# Run pytest on test_outputs.py
echo "Running pytest..."
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1
PYTEST_EXIT=$?

echo "Pytest exit code: $PYTEST_EXIT"

# Write binary reward
if [ $PYTEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "Reward written: 1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Reward written: 0"
fi