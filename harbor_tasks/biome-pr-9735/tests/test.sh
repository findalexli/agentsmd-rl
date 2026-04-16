#!/bin/bash
set -e

# Install pytest
pip3 install pytest -q --break-system-packages

# Run pytest and capture output
cd /
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/output.txt

# Write binary reward (1 if all tests passed, 0 otherwise)
if grep -qE "[0-9]+ failed|[0-9]+ passed.*ERROR|ERROR" /logs/verifier/output.txt; then
    echo "0" > /logs/verifier/reward.txt
else
    echo "1" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt