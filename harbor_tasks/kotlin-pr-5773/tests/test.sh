#!/bin/bash
set -e

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install pytest --quiet
fi

# Run tests and capture results
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (1 if all tests pass, 0 otherwise)
if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
