#!/bin/bash
set -e

# Install pytest if not already installed
pip install pytest pytest-asyncio aiosqlite -q

# Create logs directory
mkdir -p /logs/verifier

# Run the tests
cd /workspace/openhands

if python -m pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
fi
