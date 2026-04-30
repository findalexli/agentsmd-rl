#!/usr/bin/env bash
# Standardised test harness — DO NOT add task-specific logic.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest test_outputs.py -v --tb=short --ctrf=/logs/verifier/ctrf.json
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No additional rubric judging configured for this task — pytest result is
# the sole reward signal.)
