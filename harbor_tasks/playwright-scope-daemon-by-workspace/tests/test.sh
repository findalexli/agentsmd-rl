#!/bin/bash
set -e

# Run pytest and capture output
if ! python3 /tests/test_outputs.py -v 2>&1 | tee /logs/verifier/pytest.log; then
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi

# Check if all tests passed
if grep -q "FAILED" /logs/verifier/pytest.log; then
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi

# All tests passed
echo "1" > /logs/verifier/reward.txt
