#!/bin/bash
set -e

# Install pytest if needed
python3 -m pip install pytest -q 2>/dev/null || true

# Run tests and capture output
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
