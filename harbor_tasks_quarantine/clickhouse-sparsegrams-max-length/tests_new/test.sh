#!/bin/bash
set -e

# Install pytest if not available
if ! python3 -c "import pytest" 2>/dev/null; then
    pip3 install pytest -q 2>/dev/null || pip install pytest -q 2>/dev/null || true
fi

# Run the tests from the tests_new directory
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi