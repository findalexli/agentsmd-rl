#!/bin/bash

# Install pytest if not present
pip3 install pytest --break-system-packages -q 2>/dev/null || pip3 install pytest -q

# Run pytest with verbose output
python3 -m pytest /tests/test_outputs.py -v --tb=short
PYTEST_RESULT=$?

# Write reward (0 = fail, 1 = pass)
if [ $PYTEST_RESULT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
