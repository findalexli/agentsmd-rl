#!/bin/bash
# Standardized harness — DO NOT modify per task.
# Runs pytest, writes binary reward (0 or 1) to /logs/verifier/reward.txt
# based purely on pytest's exit code.

set +e

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short test_outputs.py 2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (Track 2 evaluation, if configured, runs after this script.)

exit 0
