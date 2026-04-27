#!/usr/bin/env bash
# Standard reward harness — pytest exit code → /logs/verifier/reward.txt
set -uo pipefail

mkdir -p /logs/verifier

pytest -v --tb=short --json-report --json-report-file=/logs/verifier/ctrf.json /tests/test_outputs.py
status=$?

if [ $status -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No judge configured for this task; rubric checks happen offline against
# eval_manifest.yaml.)

exit $status
