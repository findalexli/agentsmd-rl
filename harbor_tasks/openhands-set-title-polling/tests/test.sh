#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest pytest-asyncio httpx -q

# Run the tests and capture output
cd /workspace/OpenHands
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
