#!/bin/bash
set -e

# Install pytest dependencies if needed
pip install -q pytest jmespath pyyaml jsonschema 2>/dev/null || true

# Run the tests and capture output
if pytest /workspace/task/tests/test_outputs.py -v --tb=short 2>&1; then
    echo "All tests passed"
    echo "1" > /logs/verifier/reward
else
    echo "Tests failed"
    echo "0" > /logs/verifier/reward
fi
