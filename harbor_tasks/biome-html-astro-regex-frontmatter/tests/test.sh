#!/bin/bash

pip3 install --break-system-packages pytest

cd /workspace

python3 -m pytest /tests/test_outputs.py -v --tb=short --no-header
PYTEST_EXIT=$?

# Write binary reward
if [ $PYTEST_EXIT -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi
exit $PYTEST_EXIT