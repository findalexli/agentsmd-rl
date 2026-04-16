#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest -q 2>/dev/null || true

# Run the test suite
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Write binary reward based on pytest exit code
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
