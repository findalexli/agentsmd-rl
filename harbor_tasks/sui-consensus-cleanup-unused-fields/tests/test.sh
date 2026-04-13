#!/bin/bash
set -e

# Run pytest with verbose output
cd /workspace/requests || exit 1

# Run all tests
python -m pytest /tests/test_outputs.py -v 2>&1

# If we get here, all tests passed
mkdir -p /logs/verifier
echo "1" > /logs/verifier/reward.txt
