#!/bin/bash
set -e

cd /tests

# Install pytest if needed
pip install pytest --quiet --break-system-packages

# Run tests and capture output
pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (0 or 1 based on test success)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
