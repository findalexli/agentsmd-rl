#!/bin/bash
set -e

# Install pytest
pip3 install pytest --quiet

# Run tests and capture result
cd /workspace/task/tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo '{"passed": true}' > /logs/verifier/result.json
else
    echo '{"passed": false}' > /logs/verifier/result.json
fi
