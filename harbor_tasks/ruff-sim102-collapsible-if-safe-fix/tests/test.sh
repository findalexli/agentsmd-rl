#!/usr/bin/env bash
set -uo pipefail

# Install pytest if not available
pip install pytest -q

# Run all tests
if pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
