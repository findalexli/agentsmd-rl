#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# This file is boilerplate and should not be modified

cd /workspace/sui

# Install pytest if not already installed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || true

# Run the test file
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (1 if all tests pass, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
