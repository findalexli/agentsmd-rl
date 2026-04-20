#!/bin/bash
set -euo pipefail

# Run tests with verbose output
# Disable errexit temporarily to capture pytest exit code reliably
set +e
pytest /tests/test_outputs.py -v --tb=short
PYTEST_EXIT=$?
set -e

# Write binary reward (0 or 1) based on pytest exit code
if [ $PYTEST_EXIT -eq 0 ]; then
    printf '\x01' > /logs/verifier/reward.txt
else
    printf '\x00' > /logs/verifier/reward.txt
fi
