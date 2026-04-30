#!/usr/bin/env bash
set -euo pipefail

mkdir -p /logs/verifier

# Activate venv where pytest lives (matches Dockerfile)
export PATH="/opt/venv/bin:${PATH}"

cd /tests

set +e
pytest -v --tb=short -p no:cacheprovider \
  --ctrf=/logs/verifier/ctrf.json \
  test_outputs.py
PYTEST_EXIT=$?
set -e

if [ "${PYTEST_EXIT}" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# (no LLM judge for this task)
exit 0
