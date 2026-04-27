#!/bin/bash
# Standard pytest runner — writes binary reward (0/1) to /logs/verifier/reward.txt.
# DO NOT add task-specific logic here — all behavior lives in test_outputs.py.

set -u

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short test_outputs.py
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track 2 (config_edits semantic diff judgment) runs externally via the harness;
# no in-container judge is required for this markdown_authoring task.

exit 0
