#!/bin/bash
set -e

REPO="/workspace/playwright"

# Ensure /logs/verifier directory exists
mkdir -p /logs/verifier

# Set up Python environment
cd /tests

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Install dependencies if needed
if ! .venv/bin/python -c "import pytest" 2>/dev/null; then
    .venv/bin/pip install pytest
fi

# Run tests
REPO="$REPO" .venv/bin/python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Check if all tests passed
if .venv/bin/python -m pytest test_outputs.py --tb=no -q 2>&1 | grep -q "passed"; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
