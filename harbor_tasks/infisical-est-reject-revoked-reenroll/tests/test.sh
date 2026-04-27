#!/usr/bin/env bash
# Standardized test harness — runs pytest on test_outputs.py, writes binary reward
# from pytest's exit code to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short test_outputs.py
rc=$?

if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit "$rc"
