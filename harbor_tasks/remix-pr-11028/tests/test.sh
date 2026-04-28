#!/bin/bash
set -u

# Standard Harbor test runner
cd /workspace/remix

pytest /tests/test_outputs.py -v --tb=short > /tmp/pytest_out.txt 2>&1; PYTEST_RC=$?
tail -80 /tmp/pytest_out.txt

if [ $PYTEST_RC -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
echo "Reward: $(cat /logs/verifier/reward.txt)"
