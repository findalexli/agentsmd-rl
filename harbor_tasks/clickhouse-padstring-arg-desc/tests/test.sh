#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest pyyaml -q 2>/dev/null || true

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Determine reward: 1 if all tests pass, 0 otherwise
if pytest /tests/test_outputs.py --tb=no -q 2>&1 | grep -q "passed"; then
    # Check if any tests failed
    if ! pytest /tests/test_outputs.py --tb=no -q 2>&1 | grep -q "failed"; then
        echo "1" > /logs/verifier/reward.txt
    else
        echo "0" > /logs/verifier/reward.txt
    fi
else
    echo "0" > /logs/verifier/reward.txt
fi
