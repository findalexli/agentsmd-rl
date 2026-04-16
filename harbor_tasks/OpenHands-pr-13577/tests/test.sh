#!/bin/bash
set -e

# Install pytest if needed
pip install pytest pytest-asyncio httpx -q 2>/dev/null || true

# Run tests and capture output
cd /workspace/OpenHands
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt
EXIT_CODE=${PIPESTATUS[0]}

# Write reward based on pytest exit code
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
