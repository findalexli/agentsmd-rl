#!/usr/bin/env bash
# Boilerplate test runner — runs pytest on /tests/test_outputs.py and writes
# a binary reward (0/1) to /logs/verifier/reward.txt based on pytest's exit
# code. DO NOT add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest -v --tb=short --no-header test_outputs.py
PYTEST_EXIT=$?

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (Reserved for future rubric-based judging; not used for this task.)

exit 0
