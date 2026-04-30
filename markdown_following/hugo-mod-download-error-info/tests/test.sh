#!/bin/bash
# Standardized test runner: runs pytest on /tests/test_outputs.py and writes
# a binary 0/1 reward to /logs/verifier/reward.txt based purely on pytest's
# exit code. Do NOT add task-specific logic to this file.
set -u

mkdir -p /logs/verifier

cd /tests

python3 -m pytest \
    --tb=short \
    --no-header \
    -rN \
    -p no:cacheprovider \
    --ctrf /logs/verifier/ctrf.json \
    /tests/test_outputs.py
PYTEST_EXIT=$?

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_EXIT"
echo "reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# (no-op placeholder; harness LLM judge runs separately if invoked)

exit 0
