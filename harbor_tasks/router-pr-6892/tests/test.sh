#!/bin/bash
set -e

# Install pytest if not present (using --break-system-packages for node images)
python3 -m pip install pytest -q --break-system-packages 2>/dev/null || pip install pytest -q --break-system-packages 2>/dev/null || true

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
