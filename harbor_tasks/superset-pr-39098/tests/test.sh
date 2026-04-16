#!/bin/bash
set -e

# Install pytest and ruff if not present
pip install --quiet pytest ruff

# Run tests
cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Check if all tests passed
if python -m pytest test_outputs.py --tb=no -q 2>/dev/null; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
