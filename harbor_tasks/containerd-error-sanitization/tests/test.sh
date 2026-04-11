#!/bin/bash
set -e

# Install pytest if needed
if ! command -v pytest &> /dev/null; then
    pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest
fi

# Run tests - temporarily disable exit on error
cd /tests
set +e
python3 -m pytest test_outputs.py -v
EXIT_CODE=$?
set -e

# Write binary reward
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
