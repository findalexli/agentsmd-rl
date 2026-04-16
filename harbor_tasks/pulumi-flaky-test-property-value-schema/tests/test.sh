#!/bin/bash
set -e

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install --break-system-packages pytest 2>/dev/null || pip3 install pytest
fi

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
cd /workspace
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $EXIT_CODE
