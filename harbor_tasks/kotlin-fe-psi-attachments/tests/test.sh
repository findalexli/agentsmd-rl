#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests from /tmp (writable location)
cd /tmp
cp /tests/test_outputs.py .

# Run pytest and capture results
if python3 -m pytest test_outputs.py -v; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
