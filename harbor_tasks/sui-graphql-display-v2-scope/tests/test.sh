#!/bin/bash
set -e

# Install pytest using apt (system package manager)
apt-get update -qq && apt-get install -y -qq python3-pytest 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
