#!/usr/bin/env bash
# Standardized boilerplate runner — do not modify.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest -v --tb=short --ctrf /logs/verifier/ctrf.json test_outputs.py
RC=$?

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No judge invocation for markdown_authoring; Track 2 runs out-of-band.)

exit 0
