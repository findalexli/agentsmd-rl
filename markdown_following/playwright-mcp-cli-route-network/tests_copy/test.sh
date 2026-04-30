#!/bin/bash
set -e

# Harbor test runner for playwright-mcp-cli-route-network
# This runs pytest and outputs reward to /logs/verifier/reward.txt

REWARD_FILE="/logs/verifier/reward.txt"
REPO="/workspace/playwright"

# Ensure log directory exists
mkdir -p "$(dirname "$REWARD_FILE")"

cd "$REPO"

# Run pytest and capture results
echo "Running tests..."
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "All tests passed!"
    echo "1" > "$REWARD_FILE"
else
    echo "Some tests failed!"
    echo "0" > "$REWARD_FILE"
fi

# Output the reward for visibility
echo "Reward: $(cat "$REWARD_FILE")"
