#!/bin/bash
# Test runner script - standardized boilerplate
# Do not add task-specific logic here

set -e

# Install pytest if needed
pip install --quiet pytest pyyaml jmespath 2>/dev/null || true

# Run tests and capture result
cd /tests
if python -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
