#!/bin/bash
set -euo pipefail

# Install pytest and dependencies
cd /tests
pip install pytest

# Run tests and capture output
if python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log; then
    echo "1" > /logs/verifier/reward.txt
    echo "✓ All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "✗ Some tests failed"
fi
