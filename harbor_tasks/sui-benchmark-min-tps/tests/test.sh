#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || true

# Run the test file
cd /workspace/sui
pytest /tests/test_outputs.py -v --tb=short

# Write reward (1 if tests passed, 0 otherwise)
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
