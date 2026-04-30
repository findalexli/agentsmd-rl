#!/bin/bash
# Standardized test runner. Do NOT modify task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier
cd /tests

# Run pytest -> emit ctrf.json + binary reward.
python3 -m pytest test_outputs.py -v --tb=short \
    --ctrf /logs/verifier/ctrf.json
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (rubric judging is performed externally by the harness using
#  /tests/eval_manifest.yaml — no in-container judge needed)

exit "$PYTEST_RC"
