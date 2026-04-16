#!/bin/bash
set -e

# Install pytest if not available
pip install pytest -q 2>/dev/null || true

# Run tests and write binary reward
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
    exit 1
fi
