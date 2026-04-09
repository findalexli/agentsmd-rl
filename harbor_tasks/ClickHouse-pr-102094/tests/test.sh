#!/bin/bash
set -e

# Standardized test runner - do not modify

cd /workspace/ClickHouse

# Run pytest tests and capture results
if python3 -m pytest /tests/test_outputs.py -v; then
    echo '{"status": "pass", "reward": 1.0}' > /logs/verifier/result.json
else
    echo '{"status": "fail", "reward": 0.0}' > /logs/verifier/result.json
fi
