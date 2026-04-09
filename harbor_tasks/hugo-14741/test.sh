#!/bin/bash
set -e

cd /workspace/hugo

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
echo "Running tests..."
python3 /workspace/task/tests/test_outputs.py

# Write reward file
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "Tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Tests failed!"
    exit 1
fi
