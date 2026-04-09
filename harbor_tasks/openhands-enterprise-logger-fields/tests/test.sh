#!/bin/bash
set -e

# Run the test file and capture results
cd /workspace/OpenHands/enterprise
if poetry run pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
