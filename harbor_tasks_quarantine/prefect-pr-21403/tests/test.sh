#!/bin/bash
set -e

# Install pytest (prefect's cloudpickle is already compatible)
pip install --no-cache-dir pytest==8.3.4

# Run tests and write reward
cd /workspace/prefect
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/output.txt

if grep -q "PASSED" /logs/verifier/output.txt && ! grep -q "FAILED" /logs/verifier/output.txt; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
