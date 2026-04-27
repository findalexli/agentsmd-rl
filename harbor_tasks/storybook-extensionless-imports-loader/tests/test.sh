#!/usr/bin/env bash
# Standardized test runner: pytest exit code => /logs/verifier/reward.txt
set -uo pipefail

mkdir -p /logs/verifier

# pytest is preinstalled in the image; do NOT install at test time.
python3 -m pytest /tests/test_outputs.py -v --tb=short \
  --json-report --json-report-file=/logs/verifier/ctrf.json 2>/dev/null || \
python3 -m pytest /tests/test_outputs.py -v --tb=short
PYTEST_EXIT=$?

if [ "$PYTEST_EXIT" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No judge configured for this task.)

exit 0
