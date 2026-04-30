#!/bin/bash
set -euo pipefail

# Run the test suite
set +e
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1
PYTEST_EXIT=$?
set -e

# Write binary reward from pytest exit code
if [ $PYTEST_EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
