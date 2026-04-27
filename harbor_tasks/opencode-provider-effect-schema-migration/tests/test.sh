#!/bin/bash
# Standardized test runner. Writes 0/1 to /logs/verifier/reward.txt
# strictly from pytest's exit code.

set -u
mkdir -p /logs/verifier

pytest -v --tb=short \
  --ctrf=/logs/verifier/ctrf.json \
  /tests/test_outputs.py
RC=$?

if [ "$RC" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge -------------------------------------------------------------
# Optional Track 2 evaluation hook. Harness invokes if present.

exit 0
