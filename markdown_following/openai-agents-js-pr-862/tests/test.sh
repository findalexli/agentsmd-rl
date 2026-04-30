#!/usr/bin/env bash
set -euo pipefail

# Run the test suite
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1

# Write reward based on pytest exit code
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Reserved for future LLM judge integration
