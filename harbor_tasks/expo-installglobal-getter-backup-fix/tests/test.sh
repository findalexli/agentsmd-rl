#!/bin/bash
set -e

# Create log directory
mkdir -p /logs/verifier

# Install pytest using apt or pip with --break-system-packages
apt-get update -qq && apt-get install -y -qq python3-pytest 2>/dev/null || pip3 install pytest --quiet --break-system-packages

# Run the tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write reward based on test result
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
