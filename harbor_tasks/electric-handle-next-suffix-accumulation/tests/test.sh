#!/bin/bash
# Standardized boilerplate.  Reward comes solely from pytest's exit code.
# pytest + pytest-json-ctrf are baked into the Docker image's /opt/venv,
# so this script does no network I/O.
set -u

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short --ctrf /logs/verifier/ctrf.json test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "[test.sh] pytest exit=${PYTEST_RC}, reward=$(cat /logs/verifier/reward.txt)"
exit 0
