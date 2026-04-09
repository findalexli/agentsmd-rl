#!/bin/bash

cd /workspace/hugo

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || true

# Run the verifier tests and capture result
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log
TEST_EXIT=${PIPESTATUS[0]}

# Write binary reward file (1 if all tests pass, 0 otherwise)
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
