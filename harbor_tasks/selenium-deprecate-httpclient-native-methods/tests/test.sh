#!/usr/bin/env bash
# Standardized test runner. Runs pytest, writes the binary reward to
# /logs/verifier/reward.txt based purely on pytest's exit code.
set -u

mkdir -p /logs/verifier

cd /tests
python3 -m pytest -v --tb=short -p no:cacheprovider test_outputs.py 2>&1 | tee /logs/verifier/pytest.log
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "reward=$(cat /logs/verifier/reward.txt) (pytest exit=$status)"
