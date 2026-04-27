#!/usr/bin/env bash
# Standardized test runner for Harbor task evaluation.
# Reward derivation: pytest exit code → /logs/verifier/reward.txt (literal "0"/"1").
set -u

mkdir -p /logs/verifier

# Place the oracle test file inside the Superset test tree so that
# tests/unit_tests/conftest.py (which autouses an `app_context` fixture) is
# automatically applied to it. Without this, `from superset.commands...` fails
# with "App not initialized yet" during model declaration.
ORACLE_DST=/workspace/superset/tests/unit_tests/commands/sql_lab/test_pr38648_oracle.py
cp /tests/test_outputs.py "$ORACLE_DST"

cd /workspace/superset

python -m pytest \
    "$ORACLE_DST" \
    --json-report \
    --json-report-file=/logs/verifier/ctrf.json \
    --tb=short \
    -v
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No rubric judge configured for this task — eval_manifest.yaml drives
# semantic-diff judging in the harness.)
echo "pytest exit=$PYTEST_RC reward=$(cat /logs/verifier/reward.txt)"
exit 0
