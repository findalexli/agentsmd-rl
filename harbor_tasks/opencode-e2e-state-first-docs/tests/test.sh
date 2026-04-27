#!/usr/bin/env bash
# Standardized test harness — runs pytest on /tests/test_outputs.py and
# writes literal "0" or "1" to /logs/verifier/reward.txt based on the exit
# code. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

if ! python3 -c "import pytest" 2>/dev/null; then
  pip install --no-cache-dir --quiet pytest==8.3.4
fi

cd /tests
python3 -m pytest -v --tb=short test_outputs.py
status=$?

if [ $status -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "reward: $(cat /logs/verifier/reward.txt) (pytest exit=$status)"
exit 0
