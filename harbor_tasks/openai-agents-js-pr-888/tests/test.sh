#!/usr/bin/env bash
set -euo pipefail

# --- run tests ---
cd /tests
set +e
python3 -m pytest test_outputs.py -v --tb=short 2>&1
TEST_EXIT_CODE=$?
set -e

# --- write reward ---
if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (placeholder for future LLM-based evaluation)
