#!/bin/bash
set -euo pipefail

python3 -m pip install --break-system-packages pytest==8.3.4

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
echo "Judge block placeholder"
