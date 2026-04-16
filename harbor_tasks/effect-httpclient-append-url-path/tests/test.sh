#!/bin/bash
set -euo pipefail

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install -q --break-system-packages pytest
fi

# Run tests and write binary reward based on exit code
cd /tests
# Run once, capture output and exit code
output=$(python3 -m pytest test_outputs.py -v --tb=short 2>&1) || true
echo "$output" | tail -50

# Check for all tests passed (no failures in the test summary line)
# Pytest summary line looks like: "=+ 2 failed, 5 passed in Xs =+" or "=+ 7 passed in Xs =+"
if echo "$output" | grep -E "^\s*=+.*[0-9]+ failed" > /dev/null; then
    echo 0 > /logs/verifier/reward.txt
else
    echo 1 > /logs/verifier/reward.txt
fi