#!/bin/bash
# Standard test runner - DO NOT MODIFY
# Installs pytest, runs test_outputs.py, writes binary reward

set -e

# Create virtual environment if not exists
if [ ! -d "/tmp/venv" ]; then
    python3 -m venv /tmp/venv
fi

source /tmp/venv/bin/activate

# Install pytest
pip install -q pytest

# Run tests and capture result
cd /tests
if python -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
