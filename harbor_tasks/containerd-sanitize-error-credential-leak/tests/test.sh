#!/bin/bash
set -e

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest
fi

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
