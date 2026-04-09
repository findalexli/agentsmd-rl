#!/bin/bash

# Install pytest if not already installed
pip3 install pytest --quiet 2>/dev/null || pip install pytest --quiet 2>/dev/null || true

# Run the test suite
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1
TEST_EXIT=$?

# Write binary reward file
mkdir -p /logs/verifier
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
