#!/bin/bash
set -e

# Run pytest tests
python3 /tests/test_outputs.py -v 2>&1

# If we got here, all tests passed
# Write reward to the shared log directory (mounted at /logs/verifier)
mkdir -p /logs/verifier
echo "1" > /logs/verifier/reward.txt
