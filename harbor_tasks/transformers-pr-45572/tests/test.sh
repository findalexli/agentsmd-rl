#!/bin/bash
# Standard Harbor test runner. Do NOT modify.
set -euo pipefail

echo "=== Harbor Test Harness ==="
echo "Installing test-time dependencies..."
pip install pytest==8.3.4 pytest-json-report==1.5.0 --quiet 2>&1

echo "Running test_outputs.py..."
cd /workspace

set +e
python -m pytest /tests/test_outputs.py -v --tb=short --json-report --json-report-file=/logs/verifier/ctrf.json 2>&1
RC=$?
set -e

if [ $RC -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
  echo "RESULT: pass (1)"
else
  echo 0 > /logs/verifier/reward.txt
  echo "RESULT: fail (0)"
fi

# --- LLM Judge ---
echo "=== LLM Judge ==="
# Provide manifest to judge for structural checks
cp /tests/eval_manifest.yaml /logs/verifier/eval_manifest.yaml 2>/dev/null || true
echo "Judge block complete."
