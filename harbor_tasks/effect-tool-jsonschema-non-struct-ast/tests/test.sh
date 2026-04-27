#!/bin/bash
# Standardized test runner. Do not modify.

set -uo pipefail

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short --json-report --json-report-file=/logs/verifier/report.json test_outputs.py
status=$?

if [ $status -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Rubric is evaluated externally by the harness against eval_manifest.yaml.
# This block is a placeholder so the test runner remains the single source
# of the binary reward signal above.
exit $status
