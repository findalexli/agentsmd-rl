#!/bin/bash
set -e

# Run pytest and capture results
cd /workspace/ant-design

# Run tests and capture output
if python3 -m pytest /tests/test_outputs.py -v 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
    exit 1
fi
