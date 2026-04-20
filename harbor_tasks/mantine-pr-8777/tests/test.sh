#!/bin/bash
set -e

pip install --quiet pytest==8.3.4
cd /workspace
REPO=/workspace/mantine_repo python -m pytest /tests/test_outputs.py -v --tb=short --no-header -o "pythonwarnings=ignore::DeprecationWarning" 2>&1 | tee /logs/verifier/output.txt

# Binary reward: 0 if any test failed, 1 if all passed
if grep -q "FAILED" /logs/verifier/output.txt; then
    echo "0" > /logs/verifier/reward.txt
else
    echo "1" > /logs/verifier/reward.txt
fi
