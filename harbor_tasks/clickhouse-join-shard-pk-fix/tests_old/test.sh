#!/bin/bash
set -e

echo "=== Setting up test environment ==="

# Install pytest if not present
pip install pytest -q 2>/dev/null || true

# Change to tests directory
cd /workspace/task/tests

echo "=== Running tests ==="

# Run pytest with detailed output
if python -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "=== ALL TESTS PASSED ==="
    echo "1" > /logs/verifier_reward
    exit 0
else
    echo "=== SOME TESTS FAILED ==="
    echo "0" > /logs/verifier_reward
    exit 1
fi
