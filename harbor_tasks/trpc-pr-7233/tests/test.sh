#!/bin/bash

# Install pytest if not present
pip install pytest==8.3.4 --quiet

# Run tests and write binary reward (0=fail, 1=pass)
set +e
python3 -m pytest /tests/test_outputs.py -v --tb=short
pytest_result=$?
# Convert pytest exit code to binary reward: 0 (fail) -> 0, 0 (pass) -> 1
if [ $pytest_result -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi