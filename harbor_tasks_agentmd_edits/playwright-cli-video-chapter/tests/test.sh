#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Run the Python test script
python3 /tests/test_outputs.py

# The Python script writes the reward to /logs/verifier/reward.txt
# Just verify it was written
cat /logs/verifier/reward.txt
