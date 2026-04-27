#!/usr/bin/env bash
# Standardized test runner: writes binary reward to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
  --ctrf /logs/verifier/ctrf.json \
  2>&1 | tee /logs/verifier/test_output.log

if [ "${PIPESTATUS[0]}" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Rubric checks live in eval_manifest.yaml; the harness consults them post-run.
# Do not exit before this line.
echo "test.sh complete; reward=$(cat /logs/verifier/reward.txt)"
