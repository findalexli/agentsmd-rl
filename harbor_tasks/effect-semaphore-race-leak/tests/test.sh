#!/bin/bash
set -euo pipefail

pip install --break-system-packages pytest==8.3.4 1>&2

set +e
pytest /tests/test_outputs.py -v --tb=short 2>&1
PYTEST_EXIT=$?
set -e

if [ $PYTEST_EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
