#!/bin/bash
set -e

# Setup Python environment for pytest
if [ ! -d /workspace/.venv ]; then
    python3 -m venv /workspace/.venv
fi

# Install pytest if not present
/workspace/.venv/bin/pip install pytest --quiet 2>/dev/null || true

# Create log directory
mkdir -p /logs/verifier

# Run tests - tests are mounted at /tests
cd /tests
if /workspace/.venv/bin/python -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "✓ All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "✗ Some tests failed"
    exit 1
fi
