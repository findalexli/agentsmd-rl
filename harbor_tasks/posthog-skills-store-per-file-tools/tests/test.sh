#!/usr/bin/env bash
# Standardized test runner — do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

pytest test_outputs.py \
    -v \
    --tb=short \
    --json-report \
    --json-report-file=/logs/verifier/ctrf.json
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "--- pytest exit code: $PYTEST_RC ---"
echo "--- reward: $(cat /logs/verifier/reward.txt) ---"
