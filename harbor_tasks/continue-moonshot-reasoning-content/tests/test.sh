#!/bin/bash
set -e

# Install pytest
pip3 install pytest --quiet

# Run tests and capture results
cd /workspace/task/tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "{\"pass\": true, \"score\": 1.0, \"message\": \"All tests passed\"}" > /logs/verifier/result.json
else
    echo "{\"pass\": false, \"score\": 0.0, \"message\": \"Some tests failed\"}" > /logs/verifier/result.json
    exit 1
fi
