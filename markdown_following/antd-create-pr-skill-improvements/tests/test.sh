#!/usr/bin/env bash
# Standardized test harness — do NOT add task-specific logic here.
# pytest is installed in the Dockerfile (no network at test time).
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest -v --tb=short /tests/test_outputs.py
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track-2 evaluation (Gemini semantic-diff judgment based on
# eval_manifest.config_edits) happens outside the container.

exit 0
