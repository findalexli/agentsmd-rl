#!/usr/bin/env bash
# Standardised harness — runs pytest, writes binary reward to
# /logs/verifier/reward.txt from pytest's exit code only.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest -v --tb=short test_outputs.py
PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track 2 (semantic-diff judging of the markdown delta) is run by Harbor's
# rubric runner on top of the reward written above; nothing to do here.

exit 0
