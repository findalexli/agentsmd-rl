#!/bin/bash
set -e

# Install pytest
cd /workspace
echo "Installing pytest..."
pip3 install pytest --quiet --break-system-packages

# Run tests
echo "Running tests..."
cd /tests
python3 -m pytest test_outputs.py -v

# Write binary reward (all tests passed if we got here)
echo "All tests passed"
echo '{"passed": true, "reward": 1.0}' > /logs/verifier/reward.txt
