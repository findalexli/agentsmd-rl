#!/bin/bash
set -e

cd /workspace/effect-checkout

# Install pytest if needed
pip3 install pytest -q --break-system-packages

# Run tests, write binary reward
pytest -v --tb=short /tests/test_outputs.py 2>&1 | tail -50

# Write binary reward based on pytest exit code
if pytest -v --tb=short /tests/test_outputs.py; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi