#!/bin/bash
set -eo pipefail

cd /workspace/astro

# Install pytest
pip install -q pytest

# Run the tests (don't exit on failure)
set +e
pytest -v --tb=short /tests/test_outputs.py
PYTEST_EXIT=$?
set -e

# Write binary reward based on pytest exit code
mkdir -p /logs/verifier
if [ $PYTEST_EXIT -eq 0 ]; then
    printf '\x01' > /logs/verifier/reward.txt
else
    printf '\x00' > /logs/verifier/reward.txt
fi
