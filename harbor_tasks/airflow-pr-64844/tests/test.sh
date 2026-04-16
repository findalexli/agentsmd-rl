#!/bin/bash
set -e

# Install pytest if not available
pip install --quiet pytest 2>/dev/null || true

# Run the tests
cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Determine reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
