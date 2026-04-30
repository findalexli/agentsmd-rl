#!/bin/bash
# Standardized verifier entrypoint. Runs pytest on test_outputs.py and writes
# the binary reward (0 or 1) to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest -v --tb=short test_outputs.py
PYTEST_EXIT=$?

if [ "$PYTEST_EXIT" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No additional judge; reward is determined by pytest exit code only.)

exit 0
