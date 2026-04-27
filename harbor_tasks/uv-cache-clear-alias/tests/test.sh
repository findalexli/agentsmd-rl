#!/usr/bin/env bash
# Standardized test runner: pytest writes CTRF JSON for the harness, and the
# binary reward is determined by pytest's exit code.
set -u

mkdir -p /logs/verifier

PYTEST_CMD=(python3 -m pytest /tests/test_outputs.py -v --tb=short \
    --ctrf /logs/verifier/ctrf.json)

"${PYTEST_CMD[@]}"
PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No additional judge step for this task; reward is purely behavioral.)

exit 0
