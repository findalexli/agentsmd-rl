#!/bin/bash

# Install pytest
pip install pytest==8.3.4 --break-system-packages --quiet

# Run pytest and capture exit code
python -m pytest /tests/test_outputs.py -v --tb=short --no-header
TEST_RESULT=$?

# Write binary reward (1 for pass, 0 for fail)
if [ $TEST_RESULT -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi