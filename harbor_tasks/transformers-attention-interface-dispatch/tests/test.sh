#!/bin/bash
set -eo pipefail

# Standard test harness — do not add task-specific logic here.

pip install pytest==8.3.4

cd /workspace/transformers

set +e
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tail -100
PYTEST_EXIT=${PIPESTATUS[0]}
set -e

if [ $PYTEST_EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
