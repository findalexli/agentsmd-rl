#!/usr/bin/env bash
# Standardized verifier entrypoint. Runs pytest, writes binary reward.
set -uo pipefail

mkdir -p /logs/verifier

# Run the pytest suite.
cd /tests
pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=$PYTEST_EXIT, reward=$(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# Track 2 (semantic-diff judging) is performed by the harness using the
# config_edits section of eval_manifest.yaml. Nothing to do here.

exit 0
