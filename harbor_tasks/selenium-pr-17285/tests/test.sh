#!/bin/bash
set -e

mkdir -p /logs/verifier

# Install pytest if not available
pip3 install pytest -q --break-system-packages 2>/dev/null || pip3 install pytest -q 2>/dev/null || true

# Run tests
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
