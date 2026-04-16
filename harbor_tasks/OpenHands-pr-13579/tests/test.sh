#!/bin/bash
set -e

# Install pytest if not present
pip install -q pytest pytest-asyncio pytest-mock

# Run tests and write reward to /logs/verifier
mkdir -p /logs/verifier

# Run pytest and capture exit code
if pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
