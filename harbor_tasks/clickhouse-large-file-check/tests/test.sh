#!/bin/bash
set -e

# Install pytest if needed
pip install pytest --quiet

# Run tests
cd /workspace/task
timeout 120 python3 -m pytest tests/test_outputs.py -v 2>&1

# Write reward file (1 = success, 0 = failure)
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
