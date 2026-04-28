#!/usr/bin/env bash
set -euo pipefail

# --- install test deps ---
pip install --break-system-packages pytest==8.3.4 pyyaml==6.0.2 2>&1

# --- run pytest ---
cd /tests
set +e
python3 -m pytest test_outputs.py -v --tb=short 2>&1
PYTEST_EXIT=$?
set -e

# --- write reward ---
if [ $PYTEST_EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge (placeholder) ---
echo "Judge output (placeholder)" > /logs/verifier/judge_output.txt

exit 0
