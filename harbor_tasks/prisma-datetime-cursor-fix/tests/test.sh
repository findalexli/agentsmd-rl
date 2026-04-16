#!/usr/bin/env bash
# Standardized test runner — do not modify for task-specific logic.
set -euo pipefail

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"
echo "0" > "$REWARD_FILE"

# Install pytest if not present
python3 -m pip install pytest --quiet --break-system-packages 2>/dev/null || \
    python3 -m pip install pytest --quiet

# Run the tests
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$REWARD_FILE"
else
    echo "0" > "$REWARD_FILE"
fi

cat "$REWARD_FILE"
