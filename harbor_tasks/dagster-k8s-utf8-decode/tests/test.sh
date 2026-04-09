#!/bin/bash
set -e

# Install pytest if not present
pip install pytest -q

# Run the test suite and capture results
cd /tests
pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
