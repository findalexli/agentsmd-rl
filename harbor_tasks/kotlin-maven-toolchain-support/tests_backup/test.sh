#!/bin/bash
set -e

# Setup Python environment with virtual env to avoid externally-managed error
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install pytest -q

# Create logs directory
mkdir -p /logs/verifier

# Run pytest on test_outputs.py
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
