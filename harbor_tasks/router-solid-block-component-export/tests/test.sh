#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install pytest if not available
pip3 install pytest --break-system-packages -q 2>/dev/null || pip3 install pytest -q 2>/dev/null || true

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
