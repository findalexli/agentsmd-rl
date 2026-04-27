#!/usr/bin/env bash
# Standardized test runner. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

# Run pytest. ctrf plugin emits a structured report consumed by the harness.
python3 -m pytest \
    test_outputs.py \
    -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track 2 (semantic markdown diff) is evaluated externally by Gemini using
# config_edits in eval_manifest.yaml; nothing to invoke from here.

exit 0
