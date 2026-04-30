#!/bin/bash
# Standardized test runner. Writes reward to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no-op placeholder; manifest rubric is evaluated externally by the harness)
