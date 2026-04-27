#!/bin/bash
# Runs test_outputs.py and writes a binary reward (0 / 1) to
# /logs/verifier/reward.txt. The reward is taken straight from pytest's exit
# code — no grep gates, no early exit, no `|| true` on installs.

set -u

mkdir -p /logs/verifier

cd /tests

# Run pytest. ctrf reporter dumps per-test status to /logs/verifier/ctrf.json
# so the harness can audit individual checks.
python3 -m pytest \
  test_outputs.py \
  -v \
  --tb=short
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "Pytest exit code: $PYTEST_RC"
echo "Reward: $(cat /logs/verifier/reward.txt)"

exit 0
