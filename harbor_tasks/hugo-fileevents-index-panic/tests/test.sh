#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install pytest and run tests
pip3 install --quiet --break-system-packages pytest

# Run the tests
cd /tests
if pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
