#!/bin/bash
set -eo pipefail

echo "[test.sh] Installing pytest..."
pip install pytest==8.3.4 2>&1 | tail -1

echo "[test.sh] Running tests..."
set +e
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1
EXIT=$?
set -e

if [ $EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "[test.sh] reward=$(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
echo "[test.sh] Running standalone judge..."
python3 /tests/standalone_judge.py 2>&1 || true
