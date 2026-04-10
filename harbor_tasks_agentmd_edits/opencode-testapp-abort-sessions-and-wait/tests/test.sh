#!/bin/bash
set -e

echo "Installing pytest if needed..."
apt-get update -qq && apt-get install -y -qq python3-pytest > /dev/null 2>&1 || true

echo "Running tests..."
cd /tests

# Run pytest and capture exit code
if python3 -m pytest test_outputs.py -v 2>&1; then
    echo "All tests passed!"
    REWARD=1
else
    echo "Some tests failed!"
    REWARD=0
fi

# Write reward signal for verifier
mkdir -p /logs/verifier
echo "$REWARD" > /logs/verifier/reward.txt
echo "Tests completed with reward=$REWARD"
