#!/bin/bash
set -e

# Standardized test runner - DO NOT MODIFY
# This script runs pytest on test_outputs.py and writes binary reward

mkdir -p /logs/verifier

# Run pytest with verbose output and capture results
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "✓ All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "✗ Some tests failed"
fi
