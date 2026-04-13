#!/bin/bash
# Test runner script
# Mounts: /tests:ro, /logs/verifier

set -e

cd /tests
python3 test_outputs.py

# Write reward
mkdir -p /logs/verifier
echo "1" > /logs/verifier/reward.txt
