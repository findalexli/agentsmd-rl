#!/bin/bash
set -e

# Install pytest with --break-system-packages since this is a container
pip install pytest --quiet --break-system-packages

# Run tests from the mounted location
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
