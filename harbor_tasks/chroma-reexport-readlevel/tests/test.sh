#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
cd /workspace
python3 -m pytest test_outputs.py -v

# Write binary reward file (1 = success, 0 = failure)
mkdir -p /logs/verifier
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
