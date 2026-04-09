#!/bin/bash
set -e

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip install pytest pyyaml --break-system-packages 2>/dev/null || pip install pytest pyyaml
fi

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
if pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
