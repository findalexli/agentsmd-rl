#!/usr/bin/env bash
set -eo pipefail

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Run pytest and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 || true

# Calculate reward: 1 if all tests pass, 0 if any fail
# We run pytest again with junit-xml to get a definitive result
python3 -m pytest /tests/test_outputs.py --tb=no -q 2>&1 | grep -E "passed|failed|error" || true

# Run pytest with exit code to determine pass/fail
if python3 -m pytest /tests/test_outputs.py --tb=no -q 1>/dev/null 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
