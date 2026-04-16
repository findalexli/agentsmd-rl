#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q

# Run tests
cd /workspace/dagster
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Write binary reward (1 if all tests pass, 0 otherwise)
if grep -q "passed" /logs/verifier/test_output.txt && ! grep -q "failed" /logs/verifier/test_output.txt; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
