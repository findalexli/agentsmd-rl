#!/bin/bash
# Test runner script

set -e

cd /workspace/taskforge

# Run pytest on test_outputs.py
python -m pytest /tests/test_outputs.py -v 2>&1

# If we get here, all tests passed
echo "1" > /logs/verifier/reward.txt
