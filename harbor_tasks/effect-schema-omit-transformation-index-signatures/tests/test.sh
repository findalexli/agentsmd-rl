#!/usr/bin/env bash
# Standardized harness test runner: run pytest, write 0/1 reward to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
  --ctrf=/logs/verifier/ctrf.json
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (left intentionally minimal; the manifest's rubric block carries soft rules
#  and is consumed externally by the harness's judge step)

exit 0
