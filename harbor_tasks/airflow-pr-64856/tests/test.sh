#!/bin/bash
# Standardized test runner for benchmark tasks
# DO NOT MODIFY - this is boilerplate

set -e

# Install pytest if not present
pip install --quiet pytest

# Run tests and capture result
cd /tests
if pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
