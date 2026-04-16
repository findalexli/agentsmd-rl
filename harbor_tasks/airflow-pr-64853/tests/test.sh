#!/bin/bash
# Standard test harness - do not modify

# Install pytest if not present
python3 -m pip install --quiet --break-system-packages pytest 2>/dev/null || python3 -m pip install --quiet pytest 2>/dev/null || true

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
