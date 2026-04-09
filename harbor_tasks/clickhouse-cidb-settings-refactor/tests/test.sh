#!/bin/bash
set -e

# Install pytest and black
pip install pytest black -q

# Run tests (tests are mounted at /tests in the container)
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (1 if all passed, 0 if any failed)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
