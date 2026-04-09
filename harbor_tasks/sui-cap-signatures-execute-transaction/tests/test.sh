#!/bin/bash
set -e

# Standardized test runner for benchmark tasks
# Runs test_outputs.py with pytest and writes binary reward

REWARD_FILE="/logs/verifier/reward.txt"

# Ensure log directory exists
mkdir -p /logs/verifier

# Install pytest if not present (should already be in image)
python3 -m pip install pytest --quiet --break-system-packages 2>/dev/null || true

# Run the tests
cd /workspace/sui
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$REWARD_FILE"
    echo "✓ All tests passed - reward=1"
else
    echo "0" > "$REWARD_FILE"
    echo "✗ Tests failed - reward=0"
fi
