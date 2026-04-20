#!/bin/bash

# Run the test suite from /workspace (where quickwit repo lives)
cd /workspace
python -m pytest /tests/test_outputs.py -v --tb=short --disable-warnings
pytest_exit=$?

# Write reward (0 or 1) based on test success
if [ $pytest_exit -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi