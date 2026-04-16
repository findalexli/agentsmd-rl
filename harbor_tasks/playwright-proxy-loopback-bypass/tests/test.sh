#!/bin/bash
set -e

REPO=/workspace/playwright
LOGS=/logs/verifier
mkdir -p "$LOGS"

# Install ts-node for behavioral TypeScript tests
cd /workspace/playwright
npm install -g ts-node typescript 2>&1 | tail -5 || true

# Run pytest with proper Python path
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee "$LOGS/pytest_output.txt"

# Determine reward based on test results
if grep -q "passed" "$LOGS/pytest_output.txt" && ! grep -q "FAILED" "$LOGS/pytest_output.txt"; then
    echo "1" > "$LOGS/reward.txt"
else
    echo "0" > "$LOGS/reward.txt"
fi

cat "$LOGS/reward.txt"
