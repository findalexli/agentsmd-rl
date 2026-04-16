#!/bin/bash
set -e

# Create logs directory if needed
mkdir -p /logs/verifier

# Run pytest on test_outputs.py
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1

# Check if all tests passed
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
    exit 1
fi
