#!/usr/bin/env bash
# Standardized test runner. Reward comes solely from pytest's exit code.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Optional rubric-based scoring. Reaching this block requires no early exit
# above. Tools: standalone_judge.py if present.
if [ -f /tests/standalone_judge.py ]; then
  python3 /tests/standalone_judge.py /logs/verifier || true
fi

exit 0
