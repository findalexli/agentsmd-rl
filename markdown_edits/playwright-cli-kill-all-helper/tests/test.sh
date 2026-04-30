#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Change to tests directory
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="/workspace/playwright"

# Run pytest on test_outputs.py
cd "$REPO_DIR"

if ! python3 -m pytest "$TEST_DIR/test_outputs.py" -v --tb=short 2>&1; then
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi

echo "1" > /logs/verifier/reward.txt
exit 0
