#!/bin/bash
# Standardized harness test runner. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

# Pytest is already installed in the Dockerfile; no network at test time.
pytest \
    --tb=short \
    -v \
    --ctrf /logs/verifier/ctrf.json \
    /tests/test_outputs.py
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
if [ -f /tests/standalone_judge.py ]; then
    python3 /tests/standalone_judge.py || true
fi

exit 0
