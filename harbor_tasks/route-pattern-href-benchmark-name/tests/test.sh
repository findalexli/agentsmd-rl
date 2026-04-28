#!/usr/bin/env bash
set -euo pipefail

export CI=true

cd /workspace/remix

# Run the tests
if pytest /tests/test_outputs.py -v --tb=short; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# reserved for future use
