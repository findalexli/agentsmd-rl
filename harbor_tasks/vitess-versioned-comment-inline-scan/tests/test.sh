#!/usr/bin/env bash
set -uo pipefail

# Standardised binary-reward harness. Reward is derived from pytest's exit
# code only — never grep'd from output text.

mkdir -p /logs/verifier
cd /tests

pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    test_outputs.py
EXIT_CODE=$?

if [ "$EXIT_CODE" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No additional rubric judging in this scaffold — rubric is evaluated by the
# Harbor framework using eval_manifest.yaml.)

exit "$EXIT_CODE"
