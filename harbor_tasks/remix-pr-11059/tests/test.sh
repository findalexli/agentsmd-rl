#!/usr/bin/env bash
set -euo pipefail

# -- Run tests -----------------------------------------------------------
cd /workspace/remix
set +e
python3 -m pytest /tests/test_outputs.py -v --tb=short
PYTEST_EXIT=$?
set -e

# -- Write binary reward --------------------------------------------------
if [ $PYTEST_EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# -- LLM Judge (placeholder) ---------------------------------------------
echo "LLM_JUDGE_RESULT: {\"reward\": 0, \"reason\": \"placeholder\"}" > /logs/verifier/llm_judge.json
exit 0
