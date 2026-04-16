#!/bin/bash

# Run tests (pytest is pre-installed in image)
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Determine reward based on test exit code and failure detection
if grep -q "FAILED" /logs/verifier/test_output.log; then
    echo "0" > /logs/verifier/reward.txt
elif grep -q "passed" /logs/verifier/test_output.log && ! grep -q "error" /logs/verifier/test_output.log; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
