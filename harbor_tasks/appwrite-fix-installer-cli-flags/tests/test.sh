#!/usr/bin/env bash
# Standardized test runner. DO NOT add task-specific logic.
set -u

mkdir -p /logs/verifier

cd /tests
python3 -m pytest \
    --tb=short \
    -v \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ $status -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no LLM judge for this task; Track 2 (config_edits) is scored externally)

exit 0
