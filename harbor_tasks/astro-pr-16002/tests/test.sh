#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Create virtual environment for Python testing
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate

# Install pytest
pip install pytest --quiet

# Run tests and capture output
cd /tests
if python -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
