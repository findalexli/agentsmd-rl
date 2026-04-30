#!/usr/bin/env bash
# Standardised test runner: invokes pytest on test_outputs.py, writes a binary
# reward to /logs/verifier/reward.txt based purely on pytest's exit code.
set -u

mkdir -p /logs/verifier

cd /tests

# Run pytest. Reward is determined ONLY by pytest's exit code.
python3 -m pytest -v --tb=short --json-report --json-report-file=/logs/verifier/ctrf.json test_outputs.py
EXIT=$?

if [ $EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No LLM-judged checks for this task; rubric is evaluated externally.)

exit $EXIT
