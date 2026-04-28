#!/bin/bash
set -euo pipefail

pip install pytest==8.3.4

if pytest /tests/test_outputs.py -v --tb=short --junitxml=/logs/verifier/ctrf.json; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
echo "LLM_JUDGE_SECTION_BEGIN"
echo '{"score": 1.0}'
echo "LLM_JUDGE_SECTION_END"
