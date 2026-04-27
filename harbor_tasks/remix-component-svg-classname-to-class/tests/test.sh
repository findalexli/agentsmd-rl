#!/usr/bin/env bash
# Standardized test runner. Do NOT modify this file with task-specific logic.
set -u

mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt

# Activate the python venv if present (Dockerfile creates /opt/venv).
if [ -f /opt/venv/bin/activate ]; then
  # shellcheck disable=SC1091
  . /opt/venv/bin/activate
fi

cd /tmp
pytest -v --tb=short \
  -o cache_dir=/tmp/.pytest_cache \
  --ctrf=/logs/verifier/ctrf.json \
  /tests/test_outputs.py
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no rubric judge bundled with this task; reward is purely the pytest result)

exit 0
