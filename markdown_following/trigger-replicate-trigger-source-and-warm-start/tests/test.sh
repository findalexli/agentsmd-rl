#!/bin/bash
# Standardized test harness — DO NOT modify per task.
# Runs pytest on /tests/test_outputs.py and writes binary reward to
# /logs/verifier/reward.txt. Reward comes solely from pytest's exit code.

set -uo pipefail

mkdir -p /logs/verifier
cd /tests
python3 -m pytest -v --tb=short \
  --ctrf=/logs/verifier/ctrf.json \
  test_outputs.py \
  > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

cat /logs/verifier/pytest.log

if [ "$PYTEST_RC" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "[test.sh] pytest rc=$PYTEST_RC reward=$(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# (No LLM judge for this task; rubric covers it externally.)

exit 0
