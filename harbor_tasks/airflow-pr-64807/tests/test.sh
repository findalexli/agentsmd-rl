#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Test runner script - executes pytest and writes binary reward

set -e

# Ensure pytest is installed
pip install --quiet pytest pytest-mock 2>/dev/null || true

# Create logs directory if not exists
mkdir -p /logs/verifier

# Run tests and capture result
cd /tests
if python -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
