#!/bin/bash
set -e

cd /workspace/bun

# Install gcc for C++ compilation tests
if ! command -v gcc &> /dev/null; then
    apt-get update -qq && apt-get install -y -qq gcc g++ > /dev/null 2>&1
fi

# Standardized test runner for Harbor tasks
# Uses pytest for Python-based test execution

# Ensure logs directory exists
mkdir -p /logs/verifier

# Set up Python environment and run tests
python3 -m venv /tmp/test_venv
source /tmp/test_venv/bin/activate
pip install pytest pytest-timeout -q

# Run pytest and capture result
if pytest /tests/test_outputs.py -v --timeout=300 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

deactivate
