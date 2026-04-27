#!/usr/bin/env bash
# Standardised harness boilerplate. Do not add task-specific logic here.
set -u

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short test_outputs.py \
    --ctrf /logs/verifier/ctrf.json \
    > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/pytest.log

# --- LLM Judge ---
# (Reserved for rubric-based judging. Reward above is the binary pass/fail.)

exit 0
