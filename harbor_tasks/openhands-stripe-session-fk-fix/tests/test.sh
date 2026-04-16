#!/bin/bash
set -e

# Install pytest and dependencies if not present
pip install pytest pytest-asyncio sqlalchemy aiosqlite -q 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output - use pipefail to catch pytest failure
set -o pipefail
if pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "Tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Tests failed"
fi

cat /logs/verifier/reward.txt
