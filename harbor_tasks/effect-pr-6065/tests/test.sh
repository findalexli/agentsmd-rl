#!/usr/bin/env bash
set -uo pipefail

pip install pytest==8.3.4 --quiet --break-system-packages

cd /workspace/effect

set +e
python3 -m pytest /tests/test_outputs.py -v --tb=short
PYTEST_EXIT=$?
set -e

if [ $PYTEST_EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
