#!/usr/bin/env bash
# Standardized test runner. Do not modify per-task logic here.
set -uo pipefail

mkdir -p /logs/verifier

# Run pytest. Reward comes purely from pytest exit code.
cd /tests
python -m pytest -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py
PYTEST_EXIT=$?

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track 2 (Gemini config-edits judge) is run by the harness using the
# config_edits block in eval_manifest.yaml. No additional logic needed here.

exit 0
