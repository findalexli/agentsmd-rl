#!/bin/bash
set -e

# Create a virtual environment for Python dependencies
python3 -m venv /tmp/test_venv
source /tmp/test_venv/bin/activate

# Install pytest
pip install pytest --quiet

# Run tests and capture result
if pytest /tests/test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
