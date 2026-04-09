#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest -q --break-system-packages 2>/dev/null || pip3 install pytest -q

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
