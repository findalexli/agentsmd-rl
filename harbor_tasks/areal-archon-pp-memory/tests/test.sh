#!/usr/bin/env bash
# Standardized test runner.
set -uo pipefail

mkdir -p /logs/verifier

if ! command -v pytest >/dev/null 2>&1; then
    pip install --quiet pytest==8.3.4
fi

cd /tests
pytest -v --tb=short test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
:
