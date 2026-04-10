#!/bin/bash

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test suite from the mounted /tests directory
cd /tests
pytest test_outputs.py -v --tb=short

# Write binary reward (0 = fail, 1 = pass)
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
exit $RESULT
