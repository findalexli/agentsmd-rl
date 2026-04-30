#!/usr/bin/env bash
# Standardized harbor verifier: run pytest, write reward from $? only.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short test_outputs.py
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
