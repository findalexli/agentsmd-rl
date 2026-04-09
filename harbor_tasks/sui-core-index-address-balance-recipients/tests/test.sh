#!/bin/bash

# Setup Python environment
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install pytest --quiet

# Run tests - don't exit on failure so we can write reward
cd /tests
python3 -m pytest test_outputs.py -v --tb=short
TEST_EXIT=$?

# Write binary reward based on test results
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_EXIT
