#!/usr/bin/env bash
# Run the benchmark tests inside the task container.
# Reward = pytest exit code → 1 if all tests pass, else 0.
set -uo pipefail

mkdir -p /logs/verifier

# Install pytest plugins inside the venv (already provisioned in the image).
# Do NOT mask failures with `|| true` — if pytest is broken, fail loud.

cd /tests

pytest -v --tb=short \
       --ctrf /logs/verifier/ctrf.json \
       test_outputs.py
rc=$?

if [ $rc -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (placeholder — Harbor invokes the rubric judge externally on the
#  agent's diff against eval_manifest.yaml).

exit 0
