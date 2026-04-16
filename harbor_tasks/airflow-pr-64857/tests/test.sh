#!/bin/bash
# Standardized test runner for benchmark tasks
# Runs test_outputs.py and writes binary reward (0 or 1) to /logs/verifier/reward.txt

set -euo pipefail

# Ensure log directory exists
mkdir -p /logs/verifier

# Install test dependencies if not present
pip install --quiet pytest jmespath pyyaml 2>/dev/null || true

# Run tests and capture result
cd /tests
if python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

# Show the reward
echo "Reward: $(cat /logs/verifier/reward.txt)"
