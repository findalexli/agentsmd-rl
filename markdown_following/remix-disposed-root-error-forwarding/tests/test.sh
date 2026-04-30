#!/usr/bin/env bash
# Standardized test runner. Runs pytest, writes binary reward to /logs/verifier/reward.txt
# from pytest's exit code. Do not add task-specific logic.

set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No-op for this task; rubric-based judging happens out of band on the eval harness.)

exit 0
