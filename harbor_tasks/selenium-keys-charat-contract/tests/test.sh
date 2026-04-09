#!/bin/bash
set -e

# Create log directory if not exists
mkdir -p /logs/verifier

# Install pytest if not present
pip3 install pytest --quiet --break-system-packages 2>/dev/null || true

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
