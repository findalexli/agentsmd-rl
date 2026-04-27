#!/usr/bin/env bash
# Standardized test harness — runs pytest and writes 0/1 to /logs/verifier/reward.txt
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

pytest test_outputs.py -v --tb=short --json-report --json-report-file=/logs/verifier/pytest_report.json
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Reserved for downstream rubric judging; no early exit above this line.

exit $PYTEST_RC
