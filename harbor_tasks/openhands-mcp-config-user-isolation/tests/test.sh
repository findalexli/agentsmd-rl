#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install pytest if not available
pip install pytest pytest-asyncio -q 2>/dev/null || true

# Run tests from the repo directory where the actual files exist
cd /workspace/OpenHands
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
