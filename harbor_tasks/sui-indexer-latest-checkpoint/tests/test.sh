#!/bin/bash
set -e

# Install pytest if needed
pip3 install --break-system-packages pytest 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run pytest on test_outputs.py and capture results
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
