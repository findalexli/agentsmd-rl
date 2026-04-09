#!/bin/bash
set -e

cd /workspace/ant-design

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run tests and capture output
if python3 -m pytest test_outputs.py -v 2>&1; then
    echo "{\"passed\": true, \"score\": 1.0}" > /logs/verifier/result.json
else
    echo "{\"passed\": false, \"score\": 0.0}" > /logs/verifier/result.json
fi
