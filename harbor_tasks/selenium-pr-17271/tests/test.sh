#!/bin/bash
set -e

# Install pytest if not present
pip install --quiet pytest

# Run tests and capture result
cd /workspace/selenium
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Check exit code and write reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
