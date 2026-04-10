#!/bin/bash
set -e

# Install pytest if not available
pip install pytest --break-system-packages -q

# Run tests and capture output
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "PASS" > /logs/verifier/result.txt
    echo 1 > /logs/verifier/reward.txt
else
    echo "FAIL" > /logs/verifier/result.txt
    echo 0 > /logs/verifier/reward.txt
fi
