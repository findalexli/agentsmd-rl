#!/bin/bash
# Test runner script for Docker environment

# Run pytest and capture results
cd /tests
if python3 -m pytest test_outputs.py -v 2>&1; then
    # All tests passed
    mkdir -p /logs/verifier
    echo "1" > /logs/verifier/reward.txt
else
    # Some tests failed
    mkdir -p /logs/verifier
    echo "0" > /logs/verifier/reward.txt
fi
