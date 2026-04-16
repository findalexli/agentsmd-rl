#!/bin/bash
# Standard test runner - DO NOT MODIFY

set -e

# Install pytest if not available
pip install --quiet pytest pytest-timeout 2>/dev/null || true

# Run tests with verbose output
cd /workspace
python -m pytest /tests/test_outputs.py -v --tb=short --timeout=300 2>&1 | tee /logs/verifier/test_output.txt

# Check if tests passed
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
