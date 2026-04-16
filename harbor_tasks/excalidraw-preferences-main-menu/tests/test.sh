#!/bin/bash
set -e

# Create virtual environment
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate

# Install pytest
pip install pytest --quiet

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward (1 if all tests pass, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
