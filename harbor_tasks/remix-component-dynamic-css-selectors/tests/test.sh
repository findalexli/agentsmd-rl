#!/usr/bin/env bash
set -uo pipefail

# Standard pytest runner for benchmark tasks.
# DO NOT MODIFY this file — it is the same boilerplate across all tasks.

pip install pytest==8.3.4 2>/dev/null

pytest /tests/test_outputs.py -v --tb=short --color=no

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Reserved for future LLM-based evaluation extensions.
