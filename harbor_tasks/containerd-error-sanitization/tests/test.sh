#!/bin/bash
set -e

# Install pytest if needed
if ! command -v pytest &> /dev/null; then
    pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest
fi

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v

# Write binary reward
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
