#!/bin/bash
# Standard test runner for benchmark tasks
# Installs pytest, runs test_outputs.py, writes binary reward

set -e

# Install pytest and linting tools if not already installed
pip install --quiet pytest pytest-mock ruff 2>/dev/null || true

# Run the tests
cd /tests
if pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
