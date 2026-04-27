#!/usr/bin/env bash
# Standardized test runner: runs pytest on test_outputs.py and writes binary
# reward to /logs/verifier/reward.txt based on pytest's exit code.

set -u

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short \
  --ctrf /logs/verifier/ctrf.json \
  test_outputs.py 2>&1 | tee /logs/verifier/pytest.log
PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "Pytest exit: $PYTEST_EXIT, reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# (Reserved for rubric-based judging; reward already written above.)
exit 0
