#!/bin/bash
set -e

# Install prettier globally for syntax checks
npm install -g prettier 2>/dev/null || true

# Install pytest
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run pytest and capture result
python3 -m pytest /tests/test_outputs.py -v || true

# Calculate reward: 1 if all tests pass, 0 otherwise
# Count failed tests
FAILED=$(python3 -m pytest /tests/test_outputs.py --tb=no -q 2>&1 | grep -E "^FAILED" | wc -l || echo "0")
PASSED=$(python3 -m pytest /tests/test_outputs.py --tb=no -q 2>&1 | grep -E "passed" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")

if [ "$FAILED" -eq "0" ] && [ "$PASSED" -gt "0" ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
