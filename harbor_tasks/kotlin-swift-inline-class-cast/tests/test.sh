#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Create virtual environment for pytest
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate

# Install pytest
pip install pytest -q

# Run tests and capture output
cd /tests
if pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
    exit 1
fi
