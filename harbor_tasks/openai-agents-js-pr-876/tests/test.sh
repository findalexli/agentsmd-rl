#!/bin/bash
set -uo pipefail

# Run the test suite
cd /tests
python3 -m pytest test_outputs.py -v --tb=short > /logs/verifier/pytest.log 2>&1
PYTEST_EXIT_CODE=$?

# Write binary reward from pytest exit code
if [ $PYTEST_EXIT_CODE -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# This block is reached regardless of test outcome.
# The LLM judge evaluates rubric compliance from agent output.
