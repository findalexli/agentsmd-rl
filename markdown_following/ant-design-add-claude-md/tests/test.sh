#!/bin/bash
# Standard test runner: pytest exit code → /logs/verifier/reward.txt (0 or 1).
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python -m pytest \
    -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
PYTEST_EXIT=$?

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=$PYTEST_EXIT reward=$(cat /logs/verifier/reward.txt)"

# --- LLM Judge (rubric / config_edits) is invoked by harness using
# eval_manifest.yaml; this script only emits the binary track-1 reward.
exit 0
