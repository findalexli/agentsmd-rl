#!/bin/bash
set -e

cd /workspace/sui

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
python3 -m pytest /workspace/task/tests/test_outputs.py -v

# Write binary reward
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
