#!/bin/bash
# Standardized test harness — runs pytest, writes binary reward.
set -uo pipefail

mkdir -p /logs/verifier

# Run pytest with verbose output and short tracebacks.
pytest -v --tb=short --junit-xml=/logs/verifier/junit.xml \
    /tests/test_outputs.py
PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No LLM judge for this task — reward is purely test-based.)

exit $PYTEST_EXIT
