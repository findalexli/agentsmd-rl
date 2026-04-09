#!/bin/bash
set -e

cd /workspace/hugo

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || true

# Run the verifier tests
python3 -m pytest /workspace/task/tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file (1 if all tests pass, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /workspace/task/reward
else
    echo "0" > /workspace/task/reward
fi
